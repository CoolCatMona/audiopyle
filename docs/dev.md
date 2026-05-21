# Spectral Features vs Rhythm Features

## Spectral Features

Spectral features relate to the frequency content of the audio signal and are derived from the signal's spectrum. These include:
Spectral Centroid: Cetner of mass of spectrum i.e brightness of a sound
Spectral Bandwidth - Width of spectrum, range of frequencies present in sound
Spectral flatness: How noise-like a sound is, vs being tonal
Spectral Roll-off: Frequency below which a certain percentage of total spectral energy is contained. Used to distinguish between hormonic (musical) and non-harmonic sounds.
Mel-Frequency Cepstral Coefficients: Short term power spectrum of a sound, for voice recognition and music genre classification.

## Rhythm Features

Rhythm features focus on time-related aspects of the audio signal, such as time and intensity. These include Tempo, beat, rhythm patterns, and onset detection (precise moments when notes or sounds begin).

# When to look at features

## Spectral

Timbre Analysis - Color or quality of sound, distinguishing instruments or voices
Genre Classification: Different genres may have different distinct characteristics
Speech Recognition: MFCCS vital in recognizing and differentiating phonemes in speech
Sound Quality Assessment: Evaluating fidelity or clarity of audio
Music Synthesis and Transformation: Spectral features help shape the timbre
Environmental Sound Analysis: Identifying and classifying non-musical sounds (nosie, nature)

## Rhythm

Beat Tracking and Tempo Analysis: Finding the tempo of a song, or the beat
Music Composition and Production: Understanding and manipulating rhythimc structure
Dance and Movement Analysis: for synchronization
Music Genre **differentiation**: Some genres are defined by rhythmic characteristsics
Mood Analysis

## Mel-Frequency Cepstral Coefficients (MFCCs)

An n-dimensional matrix representing the power spectrum of an audio signal, captures key characteristics of the sound.

### Fourier Transforms

Fourier Transform is a mathematical model which helps to transform the signals between two different domains, such as transforming signal from frequency domain to time domain or vice versa. Useful in signal processing.

### The "Mel" Scale

The term "Mel" comes from the Mel scale, an auditory perception scale that better represents human hearing. It approximates the human ear's response more closely than the linearly spaced frequency bands, especially for lower frequencies. It is non-linear

A mel-frequency band is a segment of the scale, represented by a filter. THe filter is designed to mimic the human ear's critical bandwidths; bands of frequencies that percieve as a single auditory event or tone.

### Cepstrum

A cepstrum is the result of computing the inverse fourier transform of the logarithm of the estimated signal spectrum. The method is a tool for investigating periodic structures in frequency data.
It was derived by reversing the first four letters of spectrum.
Operations on cepstra are labeled as "Quefrency Analysis", "Liftering" or "Cepstral Analysis"

### How they are derived

Fourier Transform a windowed exerpt of a signal
Map the powers of the spectrogram onto the mel scale, using triangular overlapping unsows, or cosine overlapping windows
Take the log of the powers at each of the mel frequencies
Take the discrete cosine transform of the list of mel log powers, as if it were a signal
The MFCCs are the amplitudes of the resulting spectrum

### What they are used for

Human Auditory Characcteristics
Voice Recognition
Music Analysis - Genre Classification, instrument recognition, and mood detection
Robustness

### Shape

The output shape of the MFCC is dependant on the following:

Number of Coefficients per frame
This varies based on the applicatoin, but a common choice is to use 12 to 13
Trade off between having enough information to effectively represent the sound and not having so many ocefficients that the data becaomes noisy

Number of Frames
Depends on the length of the audio signal, the frame size (window length) and stride (hop length)
For instance, if you have a one-second audio clip and you're using a 25 ms window with a 10 ms stride, you'll end up with a larger number of frames compared to using a 40 ms window with a 15 ms stride.

### Example

Suppose you have a 10-second audio clip, and you decide to use a frame length of 25 ms with a hop length of 10 ms. This setup would result in overlapping frames. Let's assume you choose to retain 13 MFCCs per frame. The shape of the MFCC representation would be:

Number of Frames:
For a 10-second clip, with a 25 ms window and a 10 ms stride, you'd have approximately 1000 frames (10 seconds / 0.01 stride).

Number of Coefficients:
13 coefficients per frame.
So, the MFCC feature matrix for this entire clip would have a shape of approximately 1000 (frames) x 13 (coefficients).

### Problems with lengthy frames

1. Computational Complexity
2. Temporal Variability - Audio may have varying sections (intro, verse, chorus, bridge), with its own distinct characteristics. Looking at an entire audio file may dillute the distinct features, making it more challenging to extract meaningful patterns
3. Memory Consumption
4. Overfitting - May become too accustomed to training data given a small dataset, as we are tailored to specific characteristics
5. Time Alignment - Different songs may express genre characteristics at different times, using an entire audio file may garner misalignment
6. Not all parts of a song are relevant for genre classification, may want to limit to main verse or chorus

### Strategies to address problems

1. Segment audio into shorter segments
2. Aggregate Features - For each segment compute MFCC then aggregate the features over time. For instance, you could compute the mean of each coefficient over time, resulting in a single 13-dimensional vector to represent the entire audio clip. This approach is known as feature pooling.
3. Sample key parts of the audio more likely to contain genre-specific characteristics (chorus, verse)
4. Dimensionality Refuction - Use PCA to reduce dimensionality of feature set, managing memory and computational load
5. Use of delta features: Include delta and delta delta features can help capture dynamic aspects of music (i.e rate of change of MFCCs)
6. Balanced training data - Diverse and balanced across genres

## Visualization

Vertical axis represents coefficient index and the horizontal axis represents time (ms). Each point represents the magnitude of a particular coefficient at a specific time frame.

In visualizations of MFCCs, the vertical axis, reflects how the spectral energy of the audio is distributed across these perceptually-relevant frequency bands over time.

Magnitudes are the cepstral coefficients derived from the log transformed mel spectrum

Colors at each point in time represent magnitude/intensity of MFCC values. Dimensionless
Represents how the energy of the sound is distributed across different Mel-frequency bands over time.
Higher magnitude - Stronger presence / more dominant in the audio signal
Lower magnitude - lower presence / dominant
Lower order MFCCs - Captures General spectral shape. More about overall energy distribution and general shape rather htan frequency bands. May be influenced by energy in low frequency bands
High Order MFFCs - Capture finer spectral details, sensitive to change and nuance. May be influenced more by higher frequencies. Subtle and detailed aspects of sounds spectral characteristics

## Notes

MFCC is not 1 to 1 with Mel Bands
MFCC is a linear combination of the log energy values across all mel bands
First few MFCCS typically capture the general shape of the spectrum, higher order MFCCs capture finer detail
MFCC encapsulates inf from across the spectrum, but each does so in a different way.
Low order coefficients more influenced by lower mel frequency bands
higher order coefficients are more influenced by higher bands
Represent spectrum of log of spectrum

High magnitude in low order mfcc may indicate dominant features in low-mid frequency range i.e strong bass or lower pitch in speech
MFCC0 - Energy/Loudness of a signal

Higher order MFCCs may look similar because of overlapping information captured by adjacent coeefficients.

[Video on MFCCs](https://www.youtube.com/watch?v=4_SH2nfbQZ8)
[MFCC Demo](https://learn.flucoma.org/reference/mfcc/)

## Timbre

Color or Quality of a sound. Allows us to distinguish between different sources of a sound that are playing the same note at the same loudness.

## Mel Spectogram

X-axis - Time
Y-Axis - Frequency (mel scale)
Color - Magnitude
Brighter colors represent higher amplitudes (louder)
Darker colors represent lower amplitudes (quieter)

[Music Classification](https://blog.paperspace.com/music-genre-classification-using-librosa-and-pytorch/)

## What if I just have music notes?

Decompose the audio into its constituent notes, then analyze the notes

Guess the music genre based on lyrics and audio file
Look at what openai did
- https://openai.com/blog/jukebox/

https://umap-learn.readthedocs.io/en/latest/
