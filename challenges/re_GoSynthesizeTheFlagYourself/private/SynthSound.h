#pragma once

#include "../JuceLibraryCode/JuceHeader.h"

class SynthSound : public SynthesiserSound {

public: 
	bool appliesToNote(int /*midi*/) override {
		return true;
	}

	bool appliesToChannel(int /*midi_channel*/) override {
		return true;
	}

};