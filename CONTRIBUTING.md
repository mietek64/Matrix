# Contributing

Thanks for your interest — contributions of any size are welcome.

## Ways to contribute

- **Bug reports** — open an issue using the bug report template
- **Feature requests** — open an issue using the feature request template
- **Code changes** — fork, branch, pull request (see below)
- **New presets** — got a great preset config? Share it in Discussions or submit a PR

## Note on project scope

This is a personal side project. Response times may vary. That said, good PRs will be reviewed and merged.

---

## Development setup

Requires **Python 3.13**.

```bash
git clone https://github.com/mietek64/Matrix
cd Matrix
pip install rich pyfiglet
python matrix.py        # splash screen
python matrix.py -s     # test the animation
python matrix.py -c     # test the config editor
python matrix.py -p     # test the preset browser
```

No test suite — this is a visual terminal app. Manual testing across different
terminal sizes and configs is the main verification method.

---

## Making a change

1. Fork the repo and create a branch off `main`:
   ```bash
   git checkout -b feat/my-thing
   ```

2. Keep each PR focused — one feature or fix per PR.

3. **Adding a config option:**
   - Add the key + default to `DEFAULT_CONFIG`
   - Add an entry to `SCHEMA` so it appears in `-c` editor
   - Document it in `README.md` under the options table
   - If it's preset-worthy, add a preset to `BUILTIN_PRESETS`

4. **Adding a preset:**
   - Add it to `BUILTIN_PRESETS` in `matrix.py`
   - Give it a unique `id`, a good `name`, and a descriptive `desc`
   - Make sure all config keys you use exist in `DEFAULT_CONFIG`

5. Test manually, open a PR, fill in the template.

---

## Commit message style

Plain English, present tense, short:

```
add rain_tilt config option
fix title drift when ascii art has trailing spaces
update Ghost Wave preset density
```

---

## Code style

- Python 3.13, no dependencies beyond `rich` and `pyfiglet`
- No linting or formatting enforced — just match the existing style
- Keep section separators (`# ═══...`) around major blocks

---

## License

By submitting a PR you agree your contribution is released under the [MIT License](LICENSE).
