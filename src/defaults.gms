* set defaults:
AvailabilityFactor(r,t,y)$(AvailabilityFactor(r,t,y) = 0) = 1;
CapacityToActivityUnit(r,t)$(CapacityToActivityUnit(r,t) = 0) = 1;
CapacityFactor(r,t,l,y)$(CapacityFactor(r,t,l,y) = 0) = 1;
*CapacityOfOneTechnologyUnit(r,t,y) = 0;
*CapitalCostStorage(r,s,y) = 0;
*DaysInDayType(y,ls,ld) = 7;
*DaySplit(y,lh) = 0.00137;
*EmissionsPenalty(r,e,y) = 0;
*MinStorageCharge(r,s,y)    = 0;
OperationalLife(r,t)$(OperationalLife(r,t) = 0) = 1;
OperationalLifeStorage(r,s) = 99;
*RETagTechnology(r,t,y) = 0;
*RETagFuel(r,f,y) = 0;
*REMinProductionTarget(r,y) = 0;
ResidualStorageCapacity(r,s,y) = 999;
StorageLevelStart(r,s) = 999;
StorageMaxChargeRate(r,s) = 99;
StorageMaxDischargeRate(r,s) = 99;
TotalAnnualMaxCapacity(r,t,y)$(TotalAnnualMaxCapacity(r,t,y) = 0) = 99999;
* for UTOPIA:
$ontext
TotalAnnualMaxCapacity(r,'TXE','1990') = 0;
TotalAnnualMaxCapacity(r,'RHE','1990') = 0;
TotalAnnualMaxCapacity(r,'RHE','1991') = 0;
TotalAnnualMaxCapacity(r,'RHE','1992') = 0;
TotalAnnualMaxCapacity(r,'RHE','1993') = 0;
TotalAnnualMaxCapacity(r,'RHE','1994') = 0;
TotalAnnualMaxCapacity(r,'RHE','1995') = 0;
TotalAnnualMaxCapacity(r,'RHE','1996') = 0;
TotalAnnualMaxCapacity(r,'RHE','1997') = 0;
TotalAnnualMaxCapacity(r,'RHE','1998') = 0;
TotalAnnualMaxCapacity(r,'RHE','1999') = 0;
$offtext
*
TotalAnnualMaxCapacityInvestment(r,t,y)$(TotalAnnualMaxCapacityInvestment(r,t,y) = 0) = 99999;
TotalAnnualMinCapacityInvestment(r,t,y)$(TotalAnnualMinCapacityInvestment(r,t,y) = 0) = 0;
TotalTechnologyAnnualActivityUp(r,t,y)$(TotalTechnologyAnnualActivityUp(r,t,y) = 0) = 99999;
TotalTechnologyAnnualActivityLowerLimit(r,t,y)$(TotalTechnologyAnnualActivityLowerLimit(r,t,y) = 0) = 0;
TotalTechnologyModelPeriodActivityUpperLimit(r,t)$(TotalTechnologyModelPeriodActivityUpperLimit(r,t) = 0) = 99999;
TotalTechnologyModelPeriodActivityLowerLimit(r,t)$(TotalTechnologyModelPeriodActivityLowerLimit(r,t) = 0) = 0;
TradeRoute(r,rr,f,y)$(TradeRoute(r,rr,f,y) = 0) = 0;
VariableCost(r,t,m,y)$(VariableCost(r,t,m,y) = 0) = 0.00001;

DiscountRate(r) = 1;
OperationalLife(r,t) = 1;