# CogBeacon - Gamified Variations of the Wisconsin Card Sorting Test

### To connnect other sensors: 
1. Make sure your device has a python API
2. Connect your device with python
3. Call your device through CogBeacon's main.py (see lines 527-538)
4. Write your one function that binds your device the the appropriate variables captured by CogBeacon (similarly to how it is done in function readMuse(), readFrames() and SelfReport() in main.py)

### Dependencies
1. Kivy Python Cross-Platform Gui library 1.9.0 or newer

### Muse Dependencies
Install Muse tools: http://dev.choosemuse.com/tools
Install Python SDK Tools: http://das.nasophon.de/pyliblo/
Note: since we use 64-bit system for TensorFlow, check the following link for MuseSDK on 64-bit system: http://forum.choosemuse.com/t/issues-running-muselab-and-muse-io/112/20 or https://github.com/elnn/tomato/blob/master/README.md


For additional help please contact the author at: michalis.papakostas@mavs.uta.edu or mpapakos@umich.edu


### [Please also see the current version of our online available dataset](https://github.com/MikeMpapa/CogBeacon-MultiModal_Dataset_for_Cognitive_Fatigue)


More instructions along with detailed documentation will be added soon.


## Paper & Citation
Papakostas, Michalis, Akilesh Rajavenkatanarayanan, and Fillia Makedon. "CogBeacon: A Multi-Modal Dataset and Data-Collection Platform for Modeling Cognitive Fatigue." Technologies 7.2 (2019): 46.

@article{papakostas2019cogbeacon,
  title={CogBeacon: A Multi-Modal Dataset and Data-Collection Platform for Modeling Cognitive Fatigue},
  author={Papakostas, Michalis and Rajavenkatanarayanan, Akilesh and Makedon, Fillia},
  journal={Technologies},
  volume={7},
  number={2},
  pages={46},
  year={2019},
  publisher={Multidisciplinary Digital Publishing Institute}
}
