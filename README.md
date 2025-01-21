# catvox

Transcribe your voice to stdout, so you can pipe it wherever you like.

```shell
$ pip install catvox
$ catvox
If you think the sound of my voice is bad, you wanna try listening to yours
```

## pipeline branch

In this branch, we're implementing a way for the process to work as a pipeline.

### Audio sources

* a file might be piped in via stdin
* it might be provided on the command line
* it might come from a remote host
* we might have multiple mics or channels, and want to diff them or
  pre-process in some way.

### Streaming

We need to process data as streams.

Data itself comes in multiple formats, depending on downstream data
requirements. RAM usage is a killer here, needs buffered streams and
processors.

### Filtering and processing

We want to avoid work that doesn't need doing, which means:

* speech detection - speech detection is cheaper than transcription.
  so we shouldn't transcribe speech that isn't required.
* speaker identification - speaker identification has a conversion overhead
  as the data might be/is in different formats. But it reduces load on
  transcription.
* transcription might use something remote or other than Whisper in future,
  so the streams might not need to go through the same route.

### Output formats

Ideally we want to support text and audio formats on both input and output.

* Simple text output (like it is now)
* JSON (for more structured outputs / multiple speakers / translation /
  tagging)
* Subtitle formats
* TTS and voice cloning

### Implementation

* set input format(s) and output requirements
* work backwards from output to input layer
* attach stuff in a pipeline of buffered data processors

