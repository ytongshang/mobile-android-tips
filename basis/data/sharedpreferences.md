# SharedPreferences

- [彻底搞懂 SharedPreferences](https://juejin.im/entry/597446ed6fb9a06bac5bc630)

## SharedPreferences的问题

### 跨进程不安全

-   由于没有使用跨进程的锁，就算使用MODE_MULTI_PROCESS，SharedPreferences 在跨进程频繁读写有可能导致数据全部丢失。根据线上统计，SP 大约会有万分之一的损坏率

```java
private void writeToFile(MemoryCommitResult mcr, boolean isFromSyncCommit) {
        long startTime = 0;
        long existsTime = 0;
        long backupExistsTime = 0;
        long outputStreamCreateTime = 0;
        long writeTime = 0;
        long fsyncTime = 0;
        long setPermTime = 0;
        long fstatTime = 0;
        long deleteTime = 0;

        if (DEBUG) {
            startTime = System.currentTimeMillis();
        }

        boolean fileExists = mFile.exists();

        if (DEBUG) {
            existsTime = System.currentTimeMillis();

            // Might not be set, hence init them to a default value
            backupExistsTime = existsTime;
        }

        // Rename the current file so it may be used as a backup during the next read
        if (fileExists) {
            boolean needsWrite = false;

            // Only need to write if the disk state is older than this commit
            // 首先是disk的版本比memory的低才需要写入
            if (mDiskStateGeneration < mcr.memoryStateGeneration) {
                if (isFromSyncCommit) {
                    needsWrite = true;
                } else {
                    synchronized (mLock) {
                        // No need to persist intermediate states. Just wait for the latest state to
                        // be persisted.
                        // 当前的memory版本号与创建这个任务时的版本号是否是一样的
                        // 如果不一样，说明后面还有新的写文件的任务，那么就不需要写了
                        // 等后面的写文件的任务就可以了
                        if (mCurrentMemoryStateGeneration == mcr.memoryStateGeneration) {
                            needsWrite = true;
                        }
                    }
                }
            }

            if (!needsWrite) {
                mcr.setDiskWriteResult(false, true);
                return;
            }

            boolean backupFileExists = mBackupFile.exists();

            if (DEBUG) {
                backupExistsTime = System.currentTimeMillis();
            }

            // 首先是将原始文件备份，这样其它进程，至少能读到一部分数据，但可能不是最新的
            if (!backupFileExists) {
                if (!mFile.renameTo(mBackupFile)) {
                    Log.e(TAG, "Couldn't rename file " + mFile
                          + " to backup file " + mBackupFile);
                    mcr.setDiskWriteResult(false, false);
                    return;
                }
            } else {
                mFile.delete();
            }
        }

        // Attempt to write the file, delete the backup and return true as atomically as
        // possible.  If any exception occurs, delete the new file; next time we will restore
        // from the backup.
        try {
            FileOutputStream str = createFileOutputStream(mFile);

            if (DEBUG) {
                outputStreamCreateTime = System.currentTimeMillis();
            }

            if (str == null) {
                mcr.setDiskWriteResult(false, false);
                return;
            }
            XmlUtils.writeMapXml(mcr.mapToWriteToDisk, str);

            writeTime = System.currentTimeMillis();

            FileUtils.sync(str);

            fsyncTime = System.currentTimeMillis();

            str.close();
            ContextImpl.setFilePermissionsFromMode(mFile.getPath(), mMode, 0);

            if (DEBUG) {
                setPermTime = System.currentTimeMillis();
            }

            try {
                final StructStat stat = Os.stat(mFile.getPath());
                synchronized (mLock) {
                    mStatTimestamp = stat.st_mtim;
                    mStatSize = stat.st_size;
                }
            } catch (ErrnoException e) {
                // Do nothing
            }

            if (DEBUG) {
                fstatTime = System.currentTimeMillis();
            }

            // Writing was successful, delete the backup file if there is one.
            // 删除备份文件
            mBackupFile.delete();

            if (DEBUG) {
                deleteTime = System.currentTimeMillis();
            }

            mDiskStateGeneration = mcr.memoryStateGeneration;

            mcr.setDiskWriteResult(true, true);

            if (DEBUG) {
                Log.d(TAG, "write: " + (existsTime - startTime) + "/"
                        + (backupExistsTime - startTime) + "/"
                        + (outputStreamCreateTime - startTime) + "/"
                        + (writeTime - startTime) + "/"
                        + (fsyncTime - startTime) + "/"
                        + (setPermTime - startTime) + "/"
                        + (fstatTime - startTime) + "/"
                        + (deleteTime - startTime));
            }

            long fsyncDuration = fsyncTime - writeTime;
            mSyncTimes.add((int) fsyncDuration);
            mNumSync++;

            if (DEBUG || mNumSync % 1024 == 0 || fsyncDuration > MAX_FSYNC_DURATION_MILLIS) {
                mSyncTimes.log(TAG, "Time required to fsync " + mFile + ": ");
            }

            return;
        } catch (XmlPullParserException e) {
            Log.w(TAG, "writeToFile: Got exception:", e);
        } catch (IOException e) {
            Log.w(TAG, "writeToFile: Got exception:", e);
        }

        // Clean up an unsuccessfully written file
        if (mFile.exists()) {
            if (!mFile.delete()) {
                Log.e(TAG, "Couldn't clean up partially-written file " + mFile);
            }
        }
        mcr.setDiskWriteResult(false, false);
    }
```

### 加载缓慢

- SharedPreferences 文件的加载使用了异步线程，而且加载线程并没有设置线程优先级，如果这个时候主线程读取数据就需要等待文件加载线程的结束。这就导致出现主线程等待低优先级线程锁的问题，比如一个 100KB 的 SP 文件读取等待时间大约需要 50~100ms，最好提前用异步线程预加载启动过程用到的 SP 文件

```java
SharedPreferencesImpl(File file, int mode) {
        mFile = file;
        mBackupFile = makeBackupFile(file);
        mMode = mode;
        mLoaded = false;
        mMap = null;
        mThrowable = null;
        startLoadFromDisk();
    }

    // 在线程中初始化
    private void startLoadFromDisk() {
        synchronized (mLock) {
            mLoaded = false;
        }
        new Thread("SharedPreferencesImpl-load") {
            public void run() {
                loadFromDisk();
            }
        }.start();
    }

    @Override
    public int getInt(String key, int defValue) {
        synchronized (mLock) {
            // wait,如果在主线程获取数据，而数据又没有load完成，那么这一操作会阻塞主线程
            awaitLoadedLocked();
            Integer v = (Integer)mMap.get(key);
            return v != null ? v : defValue;
        }
    }

    @GuardedBy("mLock")
    private void awaitLoadedLocked() {
        if (!mLoaded) {
            // Raise an explicit StrictMode onReadFromDisk for this
            // thread, since the real read will be in a different
            // thread and otherwise ignored by StrictMode.
            BlockGuard.getThreadPolicy().onReadFromDisk();
        }
        while (!mLoaded) {
            try {
                mLock.wait();
            } catch (InterruptedException unused) {
            }
        }
        if (mThrowable != null) {
            throw new IllegalStateException(mThrowable);
        }
    }
}
```

### 全量写入

- 全量写入。无论是调用 commit() 还是 apply()，即使我们只改动其中的一个条目，都会把整个内容全部写到文件。而且即使我们多次写入同一个文件，SP 也没有将多次修改合并为一次，这也是性能差的重要原因之一

### 卡顿

- 由于提供了异步落盘的 apply 机制，在崩溃或者其他一些异常情况可能会导致数据丢失。所以当应用收到系统广播，或者被调用 onPause 等一些时机，系统会强制把所有的 SharedPreferences 对象数据落地到磁盘。如果没有落地完成，这时候主线程会被一直阻塞。这样非常容易造成卡顿，甚至是 ANR，从线上数据来看 SP 卡顿占比一般会超过 5%

```java
// ActivityThread.java
  @Override
    public void handlePauseActivity(IBinder token, boolean finished, boolean userLeaving,
            int configChanges, PendingTransactionActions pendingActions, String reason) {
        ActivityClientRecord r = mActivities.get(token);
        if (r != null) {
            if (userLeaving) {
                performUserLeavingActivity(r);
            }

            r.activity.mConfigChangeFlags |= configChanges;
            performPauseActivity(r, finished, reason, pendingActions);

            // Make sure any pending writes are now committed.
            if (r.isPreHoneycomb()) {
                QueuedWork.waitToFinish();
            }
            mSomeActivitiesChanged = true;
        }
    }

@Override
    public void handleStopActivity(IBinder token, boolean show, int configChanges,
            PendingTransactionActions pendingActions, boolean finalStateRequest, String reason) {
        final ActivityClientRecord r = mActivities.get(token);
        r.activity.mConfigChangeFlags |= configChanges;

        final StopInfo stopInfo = new StopInfo();
        performStopActivityInner(r, stopInfo, show, true /* saveState */, finalStateRequest,
                reason);

        if (localLOGV) Slog.v(
            TAG, "Finishing stop of " + r + ": show=" + show
            + " win=" + r.window);

        updateVisibility(r, show);

        // Make sure any pending writes are now committed.
        // SharedPreferences的写入
        if (!r.isPreHoneycomb()) {
            QueuedWork.waitToFinish();
        }

        stopInfo.setActivity(r);
        stopInfo.setState(r.state);
        stopInfo.setPersistentState(r.persistentState);
        pendingActions.setStopInfo(stopInfo);
        mSomeActivitiesChanged = true;
    }
```

```java
// android/app/QueuedWork.java
public static void waitToFinish() {
        long startTime = System.currentTimeMillis();
        boolean hadMessages = false;

        Handler handler = getHandler();

        synchronized (sLock) {
            if (handler.hasMessages(QueuedWorkHandler.MSG_RUN)) {
                // Delayed work will be processed at processPendingWork() below
                handler.removeMessages(QueuedWorkHandler.MSG_RUN);

                if (DEBUG) {
                    hadMessages = true;
                    Log.d(LOG_TAG, "waiting");
                }
            }

            // We should not delay any work as this might delay the finishers
            sCanDelay = false;
        }

        StrictMode.ThreadPolicy oldPolicy = StrictMode.allowThreadDiskWrites();
        try {
            processPendingWork();
        } finally {
            StrictMode.setThreadPolicy(oldPolicy);
        }

        try {
            while (true) {
                Runnable finisher;

                synchronized (sLock) {
                    finisher = sFinishers.poll();
                }

                if (finisher == null) {
                    break;
                }

                finisher.run();
            }
        } finally {
            sCanDelay = true;
        }

        synchronized (sLock) {
            long waitTime = System.currentTimeMillis() - startTime;

            if (waitTime > 0 || hadMessages) {
                mWaitTimes.add(Long.valueOf(waitTime).intValue());
                mNumWaits++;

                if (DEBUG || mNumWaits % 1024 == 0 || waitTime > MAX_WAIT_TIME_MILLIS) {
                    mWaitTimes.log(LOG_TAG, "waited: ");
                }
            }
        }
    }

    private static void processPendingWork() {
        long startTime = 0;

        if (DEBUG) {
            startTime = System.currentTimeMillis();
        }

        synchronized (sProcessingWork) {
            LinkedList<Runnable> work;

            synchronized (sLock) {
                work = (LinkedList<Runnable>) sWork.clone();
                sWork.clear();

                // Remove all msg-s as all work will be processed now
                getHandler().removeMessages(QueuedWorkHandler.MSG_RUN);
            }

            if (work.size() > 0) {
                for (Runnable w : work) {
                    w.run();
                }

                if (DEBUG) {
                    Log.d(LOG_TAG, "processing " + work.size() + " items took " +
                            +(System.currentTimeMillis() - startTime) + " ms");
                }
            }
        }
    }

    // android/app/SharedPreferencesImpl.java
    @Override
        public void apply() {
            final long startTime = System.currentTimeMillis();

            final MemoryCommitResult mcr = commitToMemory();
            final Runnable awaitCommit = new Runnable() {
                    @Override
                    public void run() {
                        try {
                            mcr.writtenToDiskLatch.await();
                        } catch (InterruptedException ignored) {
                        }

                        if (DEBUG && mcr.wasWritten) {
                            Log.d(TAG, mFile.getName() + ":" + mcr.memoryStateGeneration
                                    + " applied after " + (System.currentTimeMillis() - startTime)
                                    + " ms");
                        }
                    }
                };

            QueuedWork.addFinisher(awaitCommit);

            Runnable postWriteRunnable = new Runnable() {
                    @Override
                    public void run() {
                        awaitCommit.run();
                        QueuedWork.removeFinisher(awaitCommit);
                    }
                };

            SharedPreferencesImpl.this.enqueueDiskWrite(mcr, postWriteRunnable);

            // Okay to notify the listeners before it's hit disk
            // because the listeners should always get the same
            // SharedPreferences instance back, which has the
            // changes reflected in memory.
            notifyListeners(mcr);
        }
```