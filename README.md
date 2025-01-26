# catvox

Transcribe your voice to stdout, so you can pipe it wherever you like.

```shell
$ pip install catvox
$ catvox
If you think the sound of my voice is bad, you wanna try listening to yours
```

## pipeline branch

In this branch, we're implementing a way for the process to work as a pipeline.

Intended behaviour:

```bash
# Takes input from the mic and transcribe, send to stdout
catvox

# Transcribe files passed in as args, sequentially
catvox file1.mp3 file2.mp4

# Transcribe a file piped in from another program
arecord | catvox

# Get help on the command line options, or on a specific processor
catvox --help
catvox --help processor

# other use cases:
# * translate to another language
# * use TTS to speak the output
# * detect a speaker by voice print
# * do noise/echo cancellation and speaker separation
# * remove silence from an audio stream
```

### Streaming

We need to process data as streams.

Data itself comes in multiple formats, depending on downstream data
requirements.

### Filtering and processing

We want to avoid work that doesn't need doing, which means:

* speech detection - speech detection is cheaper than transcription.
  so we shouldn't transcribe speech that isn't required.
* speaker identification - speaker identification has a conversion overhead
  as the data might be/is in different formats. But it reduces load on
  transcription.
* transcription might use something remote or other than Whisper in future,
  so the streams might not need to go through the same route.

### Concurrency, latency, performance

Some libraries take a while to initialize, they might need to download
a model or load it into GPU memory, or wait for another computer to do that.
Other sources might need to be realtime to avoid missing data.

Quickly starting input sources, then starting downstream ones in a non-blocking
way means load times won't cause missed data.

Excessive buffering in a pipeline will increase latency, so the pipeline
solver will need to use the shortest path for each output. Ideally processors
will publish a maximum latency too, so it can be calculated. Either that or
some way inject past events into their buffer.

Performance depends on the local machine's settings, or how much resources a
user would like to consume. So there should be a way for processors to declare
reasonable defaults depending on that. I guess that means:

1. creating an rc file with sensible defaults.
2. processors should expose a way to compute defaults.
3. have `--no-processor` flags at the root level, one per processor.

### Output formats

Ideally we want to support text and audio formats on both input and output.

* Simple text output (like it is now)
* JSON (for more structured outputs / multiple speakers / translation /
  tagging)
* Subtitle formats
8
* TTS and voice cloning

### Implementation

* set input format(s) and output requirements
* work backwards from output to input layer
* attach stuff in a pipeline of buffered data processors

## Current status

Currently building out some processors for input and output, to mentally
explore pipeline resolver scenarios.

Lots of the things are stubs at the moment,
