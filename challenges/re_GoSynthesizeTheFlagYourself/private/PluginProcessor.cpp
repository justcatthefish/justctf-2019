#include "PluginProcessor.h"
#include "PluginEditor.h"

#include "defines.h"

CTFAudioProcessor::CTFAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
	: AudioProcessor(BusesProperties()
#if ! JucePlugin_IsMidiEffect
#if ! JucePlugin_IsSynth
		.withInput("Input", AudioChannelSet::stereo(), true)
#endif
		.withOutput("Output", AudioChannelSet::stereo(), true)
#endif
	), attackTime(INITIAL_ATTACK), decayTime(INITIAL_DECAY),
	   sustainTime(INITIAL_SUSTAIN), releaseTime(INITIAL_DECAY), tree(*this, nullptr)
#endif
{
	NormalisableRange<float> param1(1.0, 5000.f);
	NormalisableRange<float> param2(0.0, 1.f);
	tree.createAndAddParameter("attack", "attack", "Attack", param1, INITIAL_ATTACK, nullptr, nullptr);
	tree.createAndAddParameter("decay", "decay", "Decay", param1, INITIAL_DECAY, nullptr, nullptr);
	tree.createAndAddParameter("sustain", "sustain", "Sustain", param2, INITIAL_SUSTAIN, nullptr, nullptr);
	tree.createAndAddParameter("release", "release", "Release", param1, INITIAL_RELEASE, nullptr, nullptr);

	synth.clearVoices();
	for (int i = 0; i < 8; i++) {
		SynthVoice* v = new SynthVoice();
		v->midiQueue = &midiQueue;
		synth.addVoice(v);
	}
	synth.clearSounds();
	synth.addSound(new SynthSound());
}

CTFAudioProcessor::~CTFAudioProcessor()
{
}

const String CTFAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool CTFAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool CTFAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool CTFAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double CTFAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int CTFAudioProcessor::getNumPrograms()
{
    return 1;   
}

int CTFAudioProcessor::getCurrentProgram()
{
    return 0;
}

void CTFAudioProcessor::setCurrentProgram (int index)
{
}

const String CTFAudioProcessor::getProgramName (int index)
{
    return {};
}

void CTFAudioProcessor::changeProgramName (int index, const String& newName)
{
}

void CTFAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
	ignoreUnused(samplesPerBlock);
	lastSampleRate = sampleRate;
	synth.setCurrentPlaybackSampleRate(lastSampleRate);
}

void CTFAudioProcessor::releaseResources()
{

}

#ifndef JucePlugin_PreferredChannelConfigurations
bool CTFAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
  #if JucePlugin_IsMidiEffect
    ignoreUnused (layouts);
    return true;
  #else
    if (layouts.getMainOutputChannelSet() != AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != AudioChannelSet::stereo())
        return false;

   #if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
   #endif

    return true;
  #endif
}
#endif

void CTFAudioProcessor::processBlock (AudioBuffer<float>& buffer, MidiBuffer& midiMessages)
{
	for (int i = 0; i < synth.getNumVoices(); i++)
	{
		if (voice = dynamic_cast<SynthVoice*>(synth.getVoice(i)))
		{
			voice->getParam(*tree.getRawParameterValue("attack"),
				*tree.getRawParameterValue("decay"),
				*tree.getRawParameterValue("sustain"),
				*tree.getRawParameterValue("release"));
		}
	}
	buffer.clear();
	synth.renderNextBlock(buffer, midiMessages, 0, buffer.getNumSamples());
}

bool CTFAudioProcessor::hasEditor() const
{
    return true;
}

AudioProcessorEditor* CTFAudioProcessor::createEditor()
{
	ctfape = new CTFAudioProcessorEditor(*this);
	ctfape->startTimer(50);
	ctfape->midiQueue = &midiQueue;
	return ctfape;
}

void CTFAudioProcessor::getStateInformation (MemoryBlock& destData)
{

}

void CTFAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{

}

AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new CTFAudioProcessor();
}
