#include "PluginProcessor.h"
#include "PluginEditor.h"

#include "defines.h"

CTFAudioProcessorEditor::CTFAudioProcessorEditor (CTFAudioProcessor& p)
    : AudioProcessorEditor (&p), processor (p)
{
    setSize (400, 400);

	attackSlider.setSliderStyle(Slider::SliderStyle::LinearBar);
	attackSlider.setRange(1, 5000, 1);
	attackSlider.setValue(INITIAL_ATTACK);
	attackSlider.setTextBoxStyle(Slider::TextBoxBelow, true, 100, 40);
	attackSlider.addListener(this);
	attackLabel.setText("Attack", NotificationType::dontSendNotification);
	attackLabel.attachToComponent(&attackSlider, true);
	addAndMakeVisible(&attackSlider);

	decaySlider.setSliderStyle(Slider::SliderStyle::LinearBar);
	decaySlider.setRange(1, 5000, 1);
	decaySlider.setValue(INITIAL_DECAY);
	decaySlider.setTextBoxStyle(Slider::TextBoxBelow, true, 100, 40);
	decaySlider.addListener(this);
	decayLabel.setText("Decay", NotificationType::dontSendNotification);
	decayLabel.attachToComponent(&decaySlider, true);
	addAndMakeVisible(&decaySlider);

	sustainSlider.setSliderStyle(Slider::SliderStyle::LinearBar);
	sustainSlider.setRange(0.0, 1.0, 0.01);
	sustainSlider.setValue(INITIAL_SUSTAIN);
	sustainSlider.setTextBoxStyle(Slider::TextBoxBelow, true, 100, 40);
	sustainSlider.addListener(this);
	sustainLabel.setText("Sustain", NotificationType::dontSendNotification);
	sustainLabel.attachToComponent(&sustainSlider, true);
	addAndMakeVisible(&sustainSlider);

	releaseSlider.setSliderStyle(Slider::SliderStyle::LinearBar);
	releaseSlider.setRange(1, 5000, 1);
	releaseSlider.setValue(INITIAL_RELEASE);
	releaseSlider.setTextBoxStyle(Slider::TextBoxBelow, true, 100, 40);
	releaseSlider.addListener(this);
	releaseLabel.setText("Release", NotificationType::dontSendNotification);
	releaseLabel.attachToComponent(&releaseSlider, true);
	addAndMakeVisible(&releaseSlider);

	attackTree = new AudioProcessorValueTreeState::SliderAttachment(processor.tree, "attack", attackSlider);
	decayTree = new AudioProcessorValueTreeState::SliderAttachment(processor.tree, "decay", decaySlider);
	sustainTree = new AudioProcessorValueTreeState::SliderAttachment(processor.tree, "sustain", sustainSlider);
	releaseTree = new AudioProcessorValueTreeState::SliderAttachment(processor.tree, "release", releaseSlider);

	cyclicBuffer.resize(passLen, 0);

	flagMsg = "Flag will be there, but you have to cooperate.";
}

CTFAudioProcessorEditor::~CTFAudioProcessorEditor()
{
}

void CTFAudioProcessorEditor::paint(Graphics& g)
{
	g.fillAll(getLookAndFeel().findColour(ResizableWindow::backgroundColourId));
	g.setColour(Colours::white);
	g.setFont(15.0f);
	g.drawFittedText("ADSR Envelope:", getLocalBounds(), Justification::topLeft, 1);

	/* //for debug
	std::string tmp;
	for (int i = 0; i < cyclicBuffer.size(); i++){
		tmp += std::to_string(cyclicBuffer[i]);
		tmp += "|";
	}
	*/

    g.drawFittedText (flagMsg/*+"\n"+tmp*/, getLocalBounds(), Justification::bottom, 1);
}

void CTFAudioProcessorEditor::resized()
{
	attackSlider.setBounds(50, 30, 200, 50);
	decaySlider.setBounds(50, 80, 200, 50);
	sustainSlider.setBounds(50, 130, 200, 50);
	releaseSlider.setBounds(50, 180, 200, 50);
}

void CTFAudioProcessorEditor::sliderValueChanged(Slider* slider)
{
	if (slider == &attackSlider)
	{
		processor.attackTime = slider->getValue();
	}
	else if (slider == &decaySlider)
	{
		processor.decayTime = slider->getValue();
	}
	else if (slider == &sustainSlider)
	{
		processor.sustainTime = slider->getValue();
	}
	else if (slider == &releaseSlider)
	{
		processor.releaseTime = slider->getValue();
	}
}

void CTFAudioProcessorEditor::timerCallback() {
	repaint();

	while (!midiQueue->empty()) {
		int n = midiQueue->front();
		midiQueue->pop();

		cyclicBuffer.push_back(n);
		cyclicBuffer.erase(cyclicBuffer.begin());
		synthIt();
	}
}

void CTFAudioProcessorEditor::synthIt()
{
	vector<unsigned char> hardcoded = { 9, 2, 70, 85, 67, 8, 12, 78, 57, 71, 80, 3, 58,
		87, 79, 12, 0, 88, 12, 57, 80, 5, 60, 79, 82, 85, 89, 62, 65, 83, 66, 79 };
	std::string h[6] = {
		"714d32d45f6cb3bc336a765119cb3c4c",
		"51a96b38445ff534e3cf14c23e9c977f",
		"51a96b38445ff534e3cf14c23e9c977f",
		"bc9189406be84ec297464a514221406d",
		"4ec6aa45006dae153d94abd86b764e17",
		"51a96b38445ff534e3cf14c23e9c977f"
	};

	int hashIdx = 0;

	for (int i = 0; i < passLen;) {
		std::vector<unsigned char> tmp(3);
		std::string buf_str = "";
		for (int j = 0; j < tmp.size(); j++) {
			if (i >= passLen)
				break;
			tmp[j] = cyclicBuffer[i];
			i++;
		}
		for(int j = 0; j < tmp.size(); j++)
			buf_str += std::to_string(tmp[j]) + "|";

		MD5 hash = MD5(tmp.data(), tmp.size() * sizeof(unsigned char));
		//std::string dbg_msg = "hash: [" + std::to_string(i-tmp.size()) + "," + std::to_string(tmp.size()) + "]=";
		//dbg_msg += hash.toHexString().toStdString();
		//DBG(dbg_msg+" "+buf_str);
		if (hash.toHexString().toStdString() != h[hashIdx]) 
			return;
		hashIdx++;
	}
	MD5 hash = MD5(cyclicBuffer.data(), cyclicBuffer.size() * sizeof(unsigned char));
	std::string flag = hash.toHexString().toStdString();
	//DBG("hashed_buffer: ");
	//DBG(flag);
	for (int i = 0; i < flag.size(); i++) {
		flag[i] ^= hardcoded[i];
	}

	flagMsg = flag;
}