# PEPPER ROBOT CODES

[![NAOqi][naoqi-image]][naoqi-url] [![Python SDK ][sdk-image]][sdk-url] [![MIT][mit-image]][mit-url] [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

The motive for Pepper robot is to find a tic_tac_toe board in the environment, localise itself accordingly and then play a game of it in real time with a human.

Start the game by saying `Hi` to Pepper, it will prompt you all the way till the end of game after that. The detection of cells inside the board is made using [YOLO](https://pjreddie.com/darknet/yolo/) with a training of around 300 images. I would suggest to have one's own training with a better dataset, but for trial one can ask for its `yolo_weights` from me.

## Installation

I would highly recommend using python virtual environment for installing dependencies used in pepper programming. For installation of python virtual environment one can follow the [guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

```bash
pip install -r requirements.txt
```

One also needs to add `naoqi` a third party python package for using `qi` drivers one can find the python package [here](https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb/field_software_type/sdk/robot/nao-2).

If having a trouble while adding the python package on mac follow this [repo](https://github.com/maverickjoy/pepper-nao_python_installation_mac).

## Usage

```python
workon <virtual_env_name>

python app.py
```

## Notes

It is programmed in such a way that it supports the following features :
- Can play even on a rough hand made board.
- It will never loose a game If played legally. Game is based on : `min-max algo`
- It has heuristic learning with the help of radial enclosure of centeroids from earlier detections, for creation of board where it will try to detect board configuration even if incomplete detection occurs.
- It will try to detect, if one cheats or hasn't made a move and even if human plays computer's coin [ 'x' / 'o' ] in their move.
- Prompts to narrate the board, if human is unable to make a legal move.
- <p align="center"><img src="https://raw.githubusercontent.com/maverickjoy/pepper-tic-tac-toe/master/docs/game.jpg" width="650"></p>

---

- **Video Link**

[![TICTACTOE VIDEO][video-image-3]][video-url-3]
---

- **Other Video Links**

[![ASTHAMA SERACH VIDEO][video-image-1]][video-url-1]

[![FALL DETECTION VIDEO][video-image-2]][video-url-2]

## License

MIT License 2018 © Vikram Singh and [contributors](https://github.com/maverickjoy/pepper-tic-tac-toe/graphs/contributors)

[sdk-url]: https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb/robot/pepper-3
[sdk-image]: https://img.shields.io/badge/Python%202.7%20SDK-2.5.5-008C96.svg?style=flat

[naoqi-url]: https://developer.softbankrobotics.com/us-en/downloads/pepper
[naoqi-image]: https://img.shields.io/badge/NAOqi-2.5.5-008C96.svg

[mit-image]: https://img.shields.io/badge/license-MIT-blue.svg
[mit-url]: https://opensource.org/licenses/MIT

[video-image-1]: https://img.youtube.com/vi/lcxtWwkrp4c/0.jpg
[video-url-1]: https://youtu.be/lcxtWwkrp4c

[video-image-2]: https://img.youtube.com/vi/n_cCs7YTf70/0.jpg
[video-url-2]: https://youtu.be/n_cCs7YTf70

[video-image-3]: https://img.youtube.com/vi/a2yzU2n8eSA/0.jpg
[video-url-3]: https://youtu.be/a2yzU2n8eSA
