# password-core

Password generation core. It has no UI and no external dependencies; the GUI and CLI will import it later.

Requirements: Python 3.9 or later.

## Usage

```python
from password_core import Options, generate_password, pool_size, entropy_bits, strength_label

opts = Options(length=20, symbols=True, exclude_ambiguous=True)
pw = generate_password(opts)

bits = entropy_bits(opts.length, pool_size(opts))
print(pw, round(bits), strength_label(bits))
```

### Passphrases

```python
from password_core import PassphraseOptions, generate_passphrase, passphrase_entropy_bits

opts = PassphraseOptions(words=6, separator="-", capitalize=True, add_number=True)
print(generate_passphrase(opts))          # e.g. Lantern-Oxidize-Crumb7-Velvet-Sprout-Ample
print(passphrase_entropy_bits(opts))      # ~83 bits
```

The wordlist is the [EFF Large Wordlist](https://www.eff.org/dice) by the
Electronic Frontier Foundation, licensed under
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/us/). The 4 hyphenated
words are dropped.

## Command line

```bash
python -m password_core password --length 20 --symbols
python -m password_core passphrase --words 5 --capitalize --number
python -m password_core password --count 3 --entropy
python -m password_core passphrase --help
```

Results are written to stdout; the `--entropy` line goes to stderr, so
`python -m password_core password > out.txt` saves only the passwords.

## Security decisions

- Randomness comes from `secrets`, which uses the operating system's CSPRNG.
- At least one character from each selected class is guaranteed.
- Nothing is stored and there is no network access.

## Tests

```bash
python -m unittest -v
```
## AI
Please note that the development of this project was assisted by Artificial Intelligence (AI) tools, which were utilized to support code structuring, design implementation, and documentation refinement.