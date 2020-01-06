result = payslip.preavis
if payslip.priornotice < 0 and payslip.stc:
    result = payslip.preavis * -1
elif payslip.priornotice &lt; 0 and payslip.stc:
    result = -payslip.preavis


result=categories.DED+CNAPS_EMP+OMSI_EMP
if payslip.priornotice &lt; 0 and payslip.stc:
    result = result + categories.PREAVIS
