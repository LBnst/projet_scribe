import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 32000
CHANNELS = 1


#enregistrement audio
class Enregistreur:
    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self._frames = []
        self._stream = None

    @property
    def en_cours(self):
        return self._stream is not None

    def _callback(self, indata, frames, time_info, status):
        self._frames.append(indata.copy())

    def demarrer(self):
        if self.en_cours:
            return
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._callback,
        )
        self._stream.start()

    def arreter(self, chemin_sortie):
        if not self.en_cours:
            raise RuntimeError("Aucun enregistrement en cours.")

        self._stream.stop()
        self._stream.close()
        self._stream = None

        if not self._frames:
            raise RuntimeError("Aucun son capté (micro muet ou non autorisé ?).")

        audio = np.concatenate(self._frames, axis=0)
        sf.write(chemin_sortie, audio, self.sample_rate)

        duree = len(audio) / self.sample_rate
        return chemin_sortie, duree
