#pragma once

#include "../JuceLibraryCode/JuceHeader.h"
#include "Maximilian.h"

#include "SynthSound.h"
#include <queue>

class SynthVoice : public SynthesiserVoice
{
public:
	bool canPlaySound(SynthesiserSound* sound) override 
	{
		return dynamic_cast<SynthSound*>(sound) != nullptr;
	}

	void getParam(float attack, float decay, float sustain, float release)
	{
		env1.setAttack(attack);
		env1.setDecay(decay);
		env1.setSustain(sustain);
		env1.setRelease(release);
	}

	void pitchWheelMoved(int newPitchWheel) override
	{
	
	}

	void controllerMoved(int controllerNumber, int newControllerValue) override
	{
	
	}

	void startNote(int midiNoteNumber, float velocity, SynthesiserSound* sound,
		int currentPitchWheelPosition) override
	{
		env1.trigger = 1;
		level = velocity;
		frequency = MidiMessage::getMidiNoteInHertz(midiNoteNumber);
		midiQueue->push(midiNoteNumber);
	}

	void stopNote(float velocity, bool allowTailoff) override
	{
		env1.trigger = 0;
		if (velocity < 0.00001)
			clearCurrentNote();
	}

	void renderNextBlock(AudioBuffer<float> &outputBuffer, int startSample, int numSamples) override
	{
		for (int sample = 0; sample < numSamples; sample++)
		{
			double wave = osc1.sinewave(frequency);
			double sound = env1.adsr(wave, env1.trigger) * level;
			double filtered = filter1.lores(sound, 50, 1.0);

			for (int channel = 0; channel < outputBuffer.getNumChannels(); channel++)
			{
				outputBuffer.addSample(channel, startSample, sound);
			}

			++startSample;
		}
	}

	std::queue<int>* midiQueue;
private:
	
	double level;
	double frequency;

	maxiOsc osc1;
	maxiEnv env1;
	maxiFilter filter1;
};