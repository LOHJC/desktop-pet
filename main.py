

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
from pynput import keyboard

class PowerMeter():
    def __init__(self):
        self.cur_power_val = 0
        self.fully_charged_val = 100
    
    def charging(self, key_pressed : str):
        if (key_pressed != ""):
            self.cur_power_val = (self.cur_power_val + 1)  % self.fully_charged_val # range freom 0 to (fully_charged_val - 1)
        print(f"key_pressed: {key_pressed}, cur_power_val: {self.cur_power_val}, %: {self.cur_power_val / self.fully_charged_val}")

class KeyboardThread(QtCore.QThread):
    key_pressed = QtCore.pyqtSignal(str)
    def run(self):
        # The listener runs in its own thread
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            # Handle alphanumeric keys
            k = key.char
        except AttributeError:
            # Handle special keys (Space, Enter, etc.)
            k = str(key)
        
        self.key_pressed.emit(k)

class PetLoader(QtCore.QObject):
    # this dict has {petname, QtGui.QPixmap}
    frame_changed = QtCore.pyqtSignal(dict)
    
    def __init__(self, petname="dust"):
        super().__init__()
        self.petname = petname
        self.idle_sprites = []
        self.walk_sprites = []
        self.base_path = f"assets/{petname}"

        # for animation
        self.ori_width = 0 # original max width
        self.ori_height = 0 # original max height
        self.load_sprites()
        self.pet_scale = 3 # scale from the original
        self.step_size = 5 # pet step
        self.pos = QtCore.QPoint(0, 0)
        self.house_width = 0
        self.house_height = 0 

        self.frame_index = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(200)

        # for reading keyboard
        self.keyboard_thread = KeyboardThread()
        self.power_meter = PowerMeter()
        self.keyboard_thread.key_pressed.connect(self.power_meter.charging)
        self.keyboard_thread.start()
    
    def set_house_size(self, width, height):
        self.house_width = width
        self.house_height = height
        self.pos.setX(width - self.ori_width * self.pet_scale)
        self.pos.setY(height - self.ori_height * self.pet_scale)
    
    def resize_pixmap(self, pixmap : QtGui.QPixmap):
        new_width = int(pixmap.width() * self.pet_scale)
        new_height = int(pixmap.height() * self.pet_scale)

        # Apply resizing
        # Use Qt.FastTransformation to keep pixel
        # Use Qt.SmoothTransformation to smooth
        return pixmap.scaled(
            new_width, 
            new_height, 
            QtCore.Qt.KeepAspectRatio, 
            QtCore.Qt.FastTransformation
        )

    def update_frame(self):
        current_sprites = self.walk_sprites
        if (len(current_sprites) == 0):
            return
        
        self.frame_index = (self.frame_index + 1) % len(current_sprites)
        
        # decide the movement of the pet
        # TOFIX: currently move left and right only
        if (self.pos.x() < 0 or self.pos.x() > (self.house_width - self.ori_width * self.pet_scale)):
            transform = QtGui.QTransform()
            transform.scale(-1, 1)  # Flip horizontally
            for i in range(len(current_sprites)):
                current_sprites[i] = current_sprites[i].transformed(transform)
            self.step_size = -self.step_size # reverse direction
        
        pixmap = self.resize_pixmap(current_sprites[self.frame_index])
        self.pos.setX(self.pos.x() - self.step_size)
        
        self.frame_changed.emit({self.petname: pixmap})
    
    def load_sprites(self):
        if not(os.path.exists(self.base_path)):
            print(f"Error: folder {self.base_path} not exists!")
            return
        
        for anim_folder in os.listdir(self.base_path):
            anim_folder_path = os.path.join(self.base_path, anim_folder)
            for imgpath in sorted(os.listdir(anim_folder_path)):
                imgpath = os.path.join(anim_folder_path, imgpath)
                img = QtGui.QPixmap(imgpath)
                if (img.isNull()):
                    print(f"Error: {imgpath} is not valid")
                    return
                
                if (img.width() > self.ori_width):
                    self.ori_width = img.width()
                
                if (img.height() > self.ori_height):
                    self.ori_height = img.height()

                if (anim_folder == "idle"):
                    self.idle_sprites.append(img)
                if (anim_folder == "walk"):
                    self.walk_sprites.append(img)

class PetHouse(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # borderless, transparent and stay on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.width = 300
        self.height = 150
        self.resize(self.width, self.height)

        # for calculate window dragging
        self.mouse_drag_pos = 0

        # for the pets
        self.pets = {}
        self.pets_pixmaps = {}
    
    def paintEvent(self, a0):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Fill entire window with a color
        painter.setBrush(QtGui.QColor(100, 180, 250, 255))  # RGBA
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())
        
        # show the pets
        for petname in self.pets_pixmaps.keys():
            pixmap = self.pets_pixmaps[petname]
            pos = self.pets[petname].pos
            painter.drawPixmap(pos.x(), pos.y(), pixmap) # TOFIX: temp render at 0,0

        return super().paintEvent(a0)
    
    def mouseDoubleClickEvent(self, a0):
        # TOFIX: temp using doubleclick to close the window
        self.close()
        QtWidgets.QApplication.instance().quit()
        return super().mouseDoubleClickEvent(a0)
    
    def mousePressEvent(self, a0):
        self.mouse_drag_pos = a0.globalPos()
        return super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0):
        delta = QtCore.QPoint(a0.globalPos() - self.mouse_drag_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.mouse_drag_pos = a0.globalPos()

        return super().mouseMoveEvent(a0)
    
    def update_display(self, pixmap_dict : dict):
        # the pixmap dict has {petname, self.petname}
        petname = list(pixmap_dict.keys())[0]
        pixmap = pixmap_dict[petname]
        self.pets_pixmaps[petname] = pixmap
        self.update()

    def add_pet(self, pet : PetLoader):
        self.pets[pet.petname]= pet
        pet.frame_changed.connect(self.update_display)


if __name__ == "__main__":
    # create a borderless window
    app = QtWidgets.QApplication([])
    pethouse = PetHouse()
    pethouse.show()

    # load the pet
    dust = PetLoader()
    dust.set_house_size(pethouse.width, pethouse.height)
    pethouse.add_pet(dust)

    pass

    sys.exit(app.exec_())