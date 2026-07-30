# FlowState

> **Fork notice:** This is a public fork of [yusuf-wadi/FlowState](https://github.com/yusuf-wadi/FlowState), the original BCI application by [Yusuf Wadi](https://github.com/yusuf-wadi). Credit for the core concept and initial implementation belongs to the upstream project. Changes in this fork (docs, packaging, experiments, and related work under [kvnloo/FlowState](https://github.com/kvnloo/FlowState)) are contributions on top of that foundation—not a claim of sole authorship.

A proof of concept program that adjusts the playback speed of the YouTube video you are watching **based on how much you are paying attention**. If you are focused, it will speed up, as you are in the state of mind to acquire information at a faster rate. If you are unfocused, it will slow down, so you don't miss anything.

## This is a BCI Application

To get started, you must have a [Muse headband](https://choosemuse.com/?gad=1)

## Installation

### Backend Setup
```bash
cd backend
pipenv install
pipenv shell
```

### Frontend Setup
```bash
cd frontend
npm install
```

## To connect

### Windows

- Download Bluemuse -> [instructions](https://github.com/kowalej/BlueMuse#installation)  
- Start Bluemuse  
- If Bluetooth is enabled on your PC, you should detect it and connect

### Linux/OSX

- pip install muselsl
- run `` muselsl stream `` in a terminal instance


The Muse stream should now be flowing

Run the program 👍


[View Documentation](https://kvnloo.github.io/FlowState/)
