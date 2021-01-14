from aiida.common import AIIDA_LOGGER
import numpy as np


class ControlParser(object):
    # TODO: Decide to use ndarray or list as type of vector
    _CONTROL = {
        'allocations': {
            'nelements': {
                'type': int,
                'mandatory': True
            },
            'natoms': {
                'type': int,
                'mandatory': True
            },
            'ngrid': {
                # <len 3>
                'type': list,
                'mandatory': True
            },
            'norientations': {
                'type': int,
                'default': 0
            }
        },
        'crystal': {
            'lfactor': {
                'type': float,
                'default': 1.0
            },
            'lattvec': {
                # <3*3>
                'type': list,
                'mandatory': True
            },
            'types': {
                # <len natoms>
                'type': list,
                'mandatory': True
            },
            'elements': {
                # <len nelements>
                'type': list,
                'mandatory': True
            },
            'positions': {
                # <3 * natoms>
                'type': list,
                'mandatory': True
            },
            'masses': {
                'type': float
            },
            'gfactors': {
                'type': float
            },
            'epsilon': {
                # <3 * 3>
                # 'type': np.ndarray,
            },
            'born': {
                # <3 * 3 * natoms>
                # 'type': np.ndarray,
            },
            'scell': {
                # <len 3>
                'type': list,
                'mandatory': True
            },
            'orientations': {
                # <3 * norientations> mandatory unless norientations == 0
                'type': list,
                # 'mandatory': True
            }
        },
        'parameters': {
            'T': {},
            'T_min': {},
            'T_max': {},
            'T_step': {},
            'omega_max': {
                # 'default': 1.e100
            },
            'scalebroad': {
                'default': 1.0
            },
            'rmin': {
                # 'default': 5.0
            },
            'rmax': {
                # 'default': 505.0
            },
            'dr': {
                # 'default': 100.0
            },
            'maxiter': {
                # 'default': 1000
            },
            'nticks': {
                # 'default': 100
            },
            'eps': {
                # 'default': 1.e-5
            },
        },
        'flags': {
            'nonanalytic': {
                'default': True
            },
            'convergence': {
                'default': True
            },
            'isotopes': {
                'default': True
            },
            'autoisotopes': {
                'default': True
            },
            'nanowires': {
                'default': False
            },
            'onlyharmonic': {
                'default': False
            },
            'espresso': {
                'default': False
            }
        }
    }

    def __init__(self, data, logger=None):
        self._logger = AIIDA_LOGGER.getChild(
            self.__class__.__name__) if logger is None else logger
        self.control = data

    def _flat_vector(self, vec, sp=' '):
        return sp.join(str(i) for i in vec)

    def validate_input(self):
        valid_control = {}

        for key, inner in self.control.items():
            if key not in self._CONTROL:
                self._logger.error(f'key `{key}` is not valid in CONTRL')
                raise RuntimeError('ERROR_KEY_IN_INPUT')

            _inner = self._CONTROL[key]
            valid_inner = {}

            for inner_key, attr in inner.items():
                if inner_key not in _inner:
                    self._logger.error(
                        f'key `{inner_key}` is not valid in CONTRL.{key}')
                    raise RuntimeError('ERROR_KEY_IN_INPUT')
                _attr = _inner[inner_key]
                if 'type' in _attr and not isinstance(attr, _attr['type']):
                    self._logger.error(
                        f'key `{inner_key}` is not in valid type in CONTRL.{key}'
                    )
                    raise RuntimeError('ERROR_TYPE_IN_INPUT')
                valid_inner[inner_key] = attr

            for inner_key in _inner:
                _attr = _inner[inner_key]
                if inner_key not in inner:
                    if 'mandatory' in _attr and _attr['mandatory'] is True:
                        self._logger.error(
                            f'key `{inner_key}` is not in CONTRL.{key}')
                        raise RuntimeError('ERROR_KEY_IN_INPUT')
                    if 'default' in _attr:
                        valid_inner[inner_key] = _attr['default']
            valid_control[key] = valid_inner

        # arrange in order
        # ? only available in python version>=3.6
        valid_dict = {}
        for key in self._CONTROL:
            if key == "flags":
                continue
            if key not in valid_control:
                self._logger.error(f'key `{key}` is not in CONTRL')
                raise RuntimeError('ERROR_KEY_IN_INPUT')
            valid_dict[key] = valid_control[key]

        # orientations is mandatory unless norientations == 0
        if valid_control['allocations']['norientations'] != 0 and 'orientations' not in valid_control['crystal']:
            self._logger.error(
                'key `orientations` in CONTRL.crystal is mandatory when `norientations` in CONTRL.norientations is not zero.')
            raise RuntimeError('ERROR_KEY_IN_INPUT')
        self.valid_control = valid_dict

    def write_control(self, dist):
        try:
            self.valid_control
        except AttributeError:
            self._logger.error('Valid variable `control` does not exist.')
            raise RuntimeError('INVALID_CONTROL')
        with open(dist, 'w', encoding='utf8') as target:
            # todo try to use a more concise and human-readable way to transform format
            for name, namelist in self.valid_control.items():
                target.write(f'&{name}\n')
                for key, val in namelist.items():
                    if isinstance(val, bool):
                        target.write(
                            f'\t{key}={".true." if val else ".false."},\n')
                    elif isinstance(val, list) or isinstance(val, np.ndarray):
                        vectors = np.array(val)
                        shape = vectors.shape
                        if len(shape) == 1:
                            if isinstance(vectors[0], str):
                                _flat = ' '.join(f'"{i}"' for i in val)
                                target.write(f'\t{key}={_flat},\n')
                            else:
                                target.write(
                                    f'\t{key}={self._flat_vector(val)},\n')
                        elif len(shape) == 2:
                            # vectors = vectors.transpose()
                            for i in range(vectors.shape[0]):
                                target.write(
                                    f'\t{key}(:,{i+1})={self._flat_vector(vectors[i])},\n'
                                )
                        elif len(shape) == 3:
                            for i in range(shape[0]):
                                # matrix = np.array(vectors[i]).transpose()
                                matrix = np.array(vectors[i])
                                for j in range(matrix.shape[0]):
                                    target.write(
                                        f'\t{key}(:,{j+1},{i+1})={self._flat_vector(matrix[j])},\n'
                                    )
                        else:
                            self._logger.error(
                                f'Invalid dimension of variable in CONTROL.{name}.{key}'
                            )
                            raise RuntimeError('INVALID_CONTROL')
                    else:
                        target.write(f'\t{key}={val},\n')
                target.write('$end\n')
