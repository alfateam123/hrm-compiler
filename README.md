HRM Compiler
============

Work-in-progress compiler to have an high-level tool
to reason about problems in Human Resources Machines.

I hate pseudo-assembly.

## Install

```
virtualenv .hrm
source .hrm/bin/activate

pip install pyparsing
```

## Usage

`python main.py <script>`

## Examples

There is no formal doc about the accepted grammar (check _parser.py_),
but you can find some examples in the `examples` folder.

* script.hrm: solve the problem #9 (multiply by 8)
* script10.hrm : solve the problem #10 (multiply by 40)
