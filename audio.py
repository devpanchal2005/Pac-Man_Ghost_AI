# audio.py
import os
import math
import array
import pygame

class SoundManager:
    def __init__(self, muted=False):
        self.muted = muted
        self.last_chomp_time = 0
        self.sounds = {}
        self.channels = {}
        
        # Read the actual active mixer sample rate and channels count
        mixer_init = pygame.mixer.get_init()
        if mixer_init:
            self.sample_rate, self.sample_format, self.channels_count = mixer_init
        else:
            self.sample_rate = 44100
            self.channels_count = 2
            
        # Load file-based sounds from sounds/ directory
        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        file_mappings = {
            "beginning": "pacman_beginning.ogg",
            "chomp": "pacman_chomp.ogg",
            "death": "pacman_death.ogg",
            "eatfruit": "pacman_eatfruit.ogg",
            "eatghost": "pacman_eatghost.ogg"
        }
        
        for name, filename in file_mappings.items():
            path = os.path.join(sounds_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Error loading sound {filename}: {e}")
                    self.sounds[name] = self.make_procedural_fallback(name)
            else:
                print(f"Sound file not found: {path}")
                self.sounds[name] = self.make_procedural_fallback(name)
                
        # Generate procedural loops and tones matching the active sample rate
        self.sounds["siren_normal"] = self.make_siren(200, 400, 0.4, volume=0.1)
        self.sounds["siren_frightened"] = self.make_siren(300, 600, 0.2, volume=0.12)
        self.sounds["win"] = self.make_win_jingle(volume=0.2)
        self.sounds["gameover"] = self.make_game_over_jingle(volume=0.2)
        
        # Perform volume balance pass
        self.sounds["chomp"].set_volume(0.35)
        self.sounds["eatghost"].set_volume(0.85)
        self.sounds["eatfruit"].set_volume(0.85)
        self.sounds["death"].set_volume(0.85)
        self.sounds["beginning"].set_volume(0.7)
        
        # Assign dedicated channels to prevent collision and channel contention
        self.channels["siren"] = pygame.mixer.Channel(0)
        self.channels["beginning"] = pygame.mixer.Channel(1)
        self.channels["chomp"] = pygame.mixer.Channel(2)
        self.channels["eatfruit"] = pygame.mixer.Channel(3)
        self.channels["eatghost"] = pygame.mixer.Channel(4)
        self.channels["death"] = pygame.mixer.Channel(5)
        self.channels["win"] = pygame.mixer.Channel(6)
        self.channels["gameover"] = pygame.mixer.Channel(7)
        
        self.set_mute(self.muted)

    def make_procedural_fallback(self, name):
        if name == "beginning":
            return self.make_win_jingle()
        elif name == "chomp":
            return self.make_sine_tone(440, 0.05, 0.1)
        elif name == "death":
            return self.make_game_over_jingle()
        elif name == "eatfruit":
            return self.make_sine_tone(880, 0.15, 0.2)
        elif name == "eatghost":
            return self.make_sine_tone(660, 0.2, 0.25)
        return self.make_sine_tone(440, 0.1)

    def make_sine_tone(self, frequency, duration, volume=0.2):
        sample_rate = self.sample_rate
        num_samples = int(sample_rate * duration)
        samples = array.array('h')
        fade_len = int(sample_rate * 0.005) # 5ms fade
        
        for i in range(num_samples):
            val_float = volume * math.sin(2 * math.pi * frequency * i / sample_rate)
            
            # Apply fade in/out
            if i < fade_len:
                val_float *= (i / fade_len)
            elif i > num_samples - fade_len:
                val_float *= ((num_samples - i) / fade_len)
                
            val = int(32767 * val_float)
            if self.channels_count == 2:
                samples.append(val)
                samples.append(val)
            else:
                samples.append(val)
                
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def make_siren(self, f_start, f_end, duration, volume=0.1):
        sample_rate = self.sample_rate
        num_samples = int(sample_rate * duration)
        samples = array.array('h')
        phase = 0.0
        fade_len = int(sample_rate * 0.005) # 5ms fade
        
        for i in range(num_samples):
            t = i / num_samples
            if t < 0.5:
                freq = f_start + (f_end - f_start) * (t * 2)
            else:
                freq = f_end - (f_end - f_start) * ((t - 0.5) * 2)
            phase += 2 * math.pi * freq / sample_rate
            
            val_float = volume * math.sin(phase)
            if i < fade_len:
                val_float *= (i / fade_len)
            elif i > num_samples - fade_len:
                val_float *= ((num_samples - i) / fade_len)
                
            val = int(32767 * val_float)
            if self.channels_count == 2:
                samples.append(val)
                samples.append(val)
            else:
                samples.append(val)
                
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def make_win_jingle(self, volume=0.2):
        sample_rate = self.sample_rate
        notes = [523, 659, 784, 1046]
        samples = array.array('h')
        fade_len = int(sample_rate * 0.005) # 5ms fade
        
        for freq in notes:
            num_samples = int(sample_rate * 0.15)
            for i in range(num_samples):
                factor = 1.0 - (i / num_samples)
                if i < fade_len:
                    factor *= (i / fade_len)
                elif i > num_samples - fade_len:
                    factor *= ((num_samples - i) / fade_len)
                    
                val = int(32767 * volume * factor * math.sin(2 * math.pi * freq * i / sample_rate))
                if self.channels_count == 2:
                    samples.append(val)
                    samples.append(val)
                else:
                    samples.append(val)
                    
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def make_game_over_jingle(self, volume=0.2):
        sample_rate = self.sample_rate
        notes = [196, 165, 130]
        samples = array.array('h')
        fade_len = int(sample_rate * 0.005) # 5ms fade
        
        for freq in notes:
            num_samples = int(sample_rate * 0.3)
            for i in range(num_samples):
                factor = 1.0 - (i / num_samples)
                if i < fade_len:
                    factor *= (i / fade_len)
                elif i > num_samples - fade_len:
                    factor *= ((num_samples - i) / fade_len)
                    
                val = int(32767 * volume * factor * math.sin(2 * math.pi * freq * i / sample_rate))
                if self.channels_count == 2:
                    samples.append(val)
                    samples.append(val)
                else:
                    samples.append(val)
                    
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name, channel_name=None, loops=0):
        if self.muted:
            return
            
        # Retrigger protection for chomping sounds to ensure clean rhythmic playing
        if name == "chomp":
            now = pygame.time.get_ticks()
            if now - self.last_chomp_time < 150: # 150ms limit
                return
            self.last_chomp_time = now

        sound = self.sounds.get(name)
        if sound:
            # Route to dedicated channel if not specified
            c_name = channel_name if channel_name is not None else name
            if c_name in self.channels:
                self.channels[c_name].play(sound, loops=loops)
            else:
                sound.play(loops=loops)

    def play_siren(self, state):
        if self.muted:
            return
        siren_name = "siren_frightened" if state == "frightened" else "siren_normal"
        sound = self.sounds.get(siren_name)
        if sound:
            # Play or switch siren only when state changes, or the channel became silent
            if getattr(self, "current_siren_state", None) != state or not self.channels["siren"].get_busy():
                self.current_siren_state = state
                self.channels["siren"].play(sound, loops=-1)

    def stop_siren(self):
        self.channels["siren"].stop()
        self.current_siren_state = None

    def set_mute(self, muted):
        self.muted = muted
        master_volume = 0.0 if muted else 1.0
        for sound in self.sounds.values():
            sound.set_volume(master_volume)
        if muted:
            self.stop_siren()
            pygame.mixer.stop()
