# desktop-pet
a desktop companion

## mode
- [ ] small window mode
  - the pet is contains in the small environment
- [ ] taskbar mode
  - the pet should run around the taskbar

## todo
- [x] find asset resources
  - create using piskelapp
- [ ] show animation
  - [x] animate the pet in the window
  - [x] add scale to resize pet
  - [ ] move around in the window
    - [ ] should have some basic physics
      - [x] walk left and right
      - [x] turn when hit boundary
      - [ ] jump
- [x] generate a transparent window
- [x] init some settings
  - [x] drag
    - click and drag around the window area
  - [x] close
    - temporary double click on the window to close it
- [x] read keystrokes to have something like powermode/charging
- [ ] able to set timer for reminder

## setup
- install python
- `pip install uv`
- within this folder, `uv venv`
- activate the venv by `.venv/Scripts/activate`
- install dependencies by `uv pip install XXX`

### dependencies
- pyqt5
- pynput