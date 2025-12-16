# Debugging Report
Anan Yousef


---

## Setup

### 1. Virtual Environment
I created and set up the virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. VS Code Setup
- Installed Python extension
- Selected `.venv` as the Python interpreter
- Created `.vscode/launch.json` with two configurations:
  - Django: runserver
  - Django: manage.py test (debug)

---

## Bug 1: AttributeError

### The Problem
Line 29: `query = request.GET.get('q').strip()`

When I went to `/buggy/` without a query parameter, it crashed because `get('q')` returned `None`, and you can't call `.strip()` on `None`.

### How I Found It
1. Set breakpoint on line 29
2. Started debugger (F5)
3. Went to `http://127.0.0.1:8000/buggy/`
4. Pressed F10 and saw the error: `AttributeError: 'NoneType' object has no attribute 'strip'`
5. Checked Variables pane - saw `request.GET.get('q')` was `None`

### The Fix
```python
query = (request.GET.get('q') or "").strip()
```
Now if `q` is missing, it uses an empty string instead of `None`.

---

## Bug 2: Wrong Comparison

### The Problem
Line 34: `if field_filter is not 'All':`

Using `is not` checks if two objects are the same in memory, not if they're equal. This doesn't work reliably for strings.

### How I Found It
1. Set breakpoint on line 34
2. Went to `/buggy/?q=ai&field=All`
3. In Variables pane, saw `field_filter = 'All'`
4. The condition still ran sometimes even though it shouldn't
5. Realized `is not` was comparing memory addresses, not values

### The Fix
```python
if field_filter != 'All':
```
Changed to `!=` which compares the actual string values.

---

## Bug 3: Typo in Dictionary Key

### The Problem
Line 38: `return query.lower() in p['title'].lower() or query.lower() in p['descriptionn'].lower()`

The key is spelled `'descriptionn'` with two n's, but it should be `'description'`.

### How I Found It
1. Set breakpoint in the predicate function
2. Went to `/buggy/?q=city`
3. Used F11 to step into the function
4. Got error: `KeyError: 'descriptionn'`
5. Looked at the project dictionary - the key was `'description'` not `'descriptionn'`

### The Fix
```python
return query.lower() in p['title'].lower() or query.lower() in p['description'].lower()
```
Fixed the typo - removed the extra 'n'.

---

## Debugging Tools I Used

- **Breakpoints**: Paused code at specific lines
- **F10 (Step Over)**: Run one line at a time
- **F11 (Step Into)**: Go inside function calls
- **Variables Pane**: See what values variables have
- **Debug Console**: Test code while debugging

--
