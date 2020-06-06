*
* OSEMOSYS 2011.07.07 conversion to GAMS by Ken Noble, Noble-Soft Systems - August 2012
* OSEMOSYS 2017.11.08 update by Thorsten Burandt, Konstantin L�ffler and Karlo Hainsch, TU Berlin (Workgroup for Infrastructure Policy) - October 2017
*
* Files required are:
* osemosys.gms (this file)
* osemosys_dec.gms
* utopia_data.txt
* osemosys_equ.gms
*
* To run this GAMS version of OSeMOSYS on your PC:
* 1. YOU MUST HAVE GAMS VERSION 22.7 OR HIGHER INSTALLED.
* This is because OSeMOSYS has some parameter, variable and equation names
* that exceed 31 characters in length, and GAMS versions prior to 22.7 have
* a limit of 31 characters on the length of such names.
* 2. Ensure that your PATH contains the GAMS Home Folder.
* 3. Place all 4 of the above files in a convenient folder,
* open a Command Prompt window in this folder, and enter:
* gams osemosys.gms
* 4. You should find that you get an optimal value of 29446.861.
* 5. Some results are created in file SelResults.CSV that you can view in Excel.
*
* declarations for sets, parameters, variables
$offlisting
$include osemosys_dec.gms
* specify Utopia Model data

$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
*$gdxin apec.gdx
$load DAILYTIMEBRACKET DAYTYPE REGION YEAR FUEL MODE_OF_OPERATION EMISSION SEASON STORAGE TECHNOLOGY TIMESLICE InputActivityRatio AccumulatedAnnualDemand AnnualEmissionLimit AnnualExogenousEmission AvailabilityFactor CapacityFactor CapacityofOneTechnologyUnit CapacityToActivityUnit CapitalCost CapitalCostStorage Conversionld Conversionlh Conversionls DaysInDayType DaySplit DepreciationMethod DiscountRate EmissionActivityRatio EmissionsPenalty FixedCost MinStorageCharge ModelPeriodEmissionLimit ModelPeriodExogenousEmission OperationalLife OperationalLifeStorage OutputActivityRatio REMinProductionTarget ReserveMargin ReserveMarginTagFuel ReserveMarginTagTechnology ResidualCapacity ResidualStorageCapacity RETagFuel RETagTechnology SpecifiedAnnualDemand SpecifiedDemandProfile StorageLevelStart StorageMaxChargeRate StorageMaxDischargeRate TechnologyFromStorage TechnologyToStorage TotalAnnualMaxCapacity TotalAnnualMaxCapacityInvestment TotalAnnualMinCapacity TotalTechnologyAnnualActivityUpperLimit TotalTechnologyModelPeriodActivityLowerLimit TotalTechnologyModelPeriodActivityUpperLimit TotalAnnualMinCapacityInvestment TotalTechnologyAnnualActivityLowerLimit TradeRoute VariableCost YearSplit
$gdxin

$include defaults.gms

*$exit

*$include utopia_data.txt
* define model equations
$offlisting
$include osemosys_equ.gms

* solve the model
*option lp = cbc
model osemosys /all/;
*$exit

option limrow=0, limcol=0, solprint=off;
osemosys.optfile=1;
solve osemosys minimizing z using LP;
* create results in file SelResults.CSV
*$include osemosys_res.gms
