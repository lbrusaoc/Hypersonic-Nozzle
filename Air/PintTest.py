import pint
ureg = pint.UnitRegistry()
ureg.formatter.default_format = "~P"
b_SI = (ureg.pascal * ureg.second / ureg.degK**0.5)
b_Imp = (ureg.lbf * ureg.second / (ureg.foot**2 * ureg.degR**0.5))
print(b_SI)
print(b_Imp)
B = 2.27E-08 * b_Imp
print(B.to(b_SI))