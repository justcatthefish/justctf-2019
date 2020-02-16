#pragma once

#include "../JuceLibraryCode/JuceHeader.h"
#include "PluginProcessor.h"

class CTFAudioProcessorEditor : public AudioProcessorEditor, public Slider::Listener, public Timer
{
public:
    CTFAudioProcessorEditor (CTFAudioProcessor&);
    ~CTFAudioProcessorEditor();

    void paint (Graphics&) override;
    void resized() override;

	void sliderValueChanged(Slider* slider) override;
	std::queue<int>* midiQueue = nullptr;

	void timerCallback() override;

private:
    CTFAudioProcessor& processor;

	ScopedPointer<AudioProcessorValueTreeState::SliderAttachment> attackTree;
	ScopedPointer<AudioProcessorValueTreeState::SliderAttachment> decayTree;
	ScopedPointer<AudioProcessorValueTreeState::SliderAttachment> sustainTree;
	ScopedPointer<AudioProcessorValueTreeState::SliderAttachment> releaseTree;
	Slider attackSlider;
	Slider decaySlider;
	Slider sustainSlider;
	Slider releaseSlider;
	Label attackLabel;
	Label decayLabel;
	Label sustainLabel;
	Label releaseLabel;

	String flagMsg;

	const int passLen = 18;
	std::vector<unsigned char> cyclicBuffer;
	void synthIt();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (CTFAudioProcessorEditor)
};
