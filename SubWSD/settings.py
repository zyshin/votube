USE_LOCAL_MODEL = False
# USE_LOCAL_MODEL = True
CREATE_SNAPSHOT = False
# CREATE_SNAPSHOT = True
SAVE_SENTS_TO_DB = False
# SAVE_SENTS_TO_DB = True
SNAPSHOT_SETTINGS = {
    'snapshot_dir': '/data/disk1/grayluck/movies/snapshots/',
    'movie_dir': '/data/disk1/grayluck/movies/mp4/',
    'ffmpeg': '/data/disk1/grayluck/movies/ffmpeg/ffmpeg -loglevel panic -noaccurate_seek'
}
