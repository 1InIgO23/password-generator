# password-core

Núcleo de generación de contraseñas. No tiene interfaz ni dependencias externas; la UI y la CLI lo importarán más adelante.

Requisitos: Python 3.9 o superior.

## Uso

```python
from password_core import Options, generate_password, pool_size, entropy_bits, strength_label

opts = Options(length=20, symbols=True, exclude_ambiguous=True)
pw = generate_password(opts)

bits = entropy_bits(opts.length, pool_size(opts))
print(pw, round(bits), strength_label(bits))
```

### Frases de paso

```python
from password_core import PassphraseOptions, generate_passphrase, passphrase_entropy_bits

opts = PassphraseOptions(words=6, separator="-", capitalize=True, add_number=True)
print(generate_passphrase(opts))          # p. ej. Lantern-Oxidize-Crumb7-Velvet-Sprout-Ample
print(passphrase_entropy_bits(opts))      # ~83 bits
```

La lista de palabras es la [EFF Large Wordlist](https://www.eff.org/dice) de la
Electronic Frontier Foundation, con licencia
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/us/). Se descartan las
4 palabras que llevan guion.

## Decisiones de seguridad

- La aleatoriedad viene de `secrets`, que usa el CSPRNG del sistema.
- Se garantiza al menos un carácter de cada clase seleccionada.
- No se guarda nada y no hay red.

## Tests

```bash
python -m unittest -v
```
