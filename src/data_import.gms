$onecho > task1.txt
set=YEAR rng=YEAR!A2 Rdim=1
set=TECHNOLOGY rng=TECHNOLOGY!A2 Rdim=1
set=REGION rng=REGION!A2 Rdim=1
set=FUEL rng=FUEL! rdim=1
par=OperationalLife rng=OperationalLife! rdim=2
$offecho

$call GDXXRW C:\Users\david\GitHub\aperc-osemosys\data\master-data-UTOPIA.xlsx @task1.txt trace=3
$gdxin master-data-UTOPIA.gdx
$load YEAR TECHNOLOGY REGION FUEL OperationalLife
$gdxin

$onecho > task2.txt
par=AccumulatedAnnualDemand rng=AccumulatedAnnualDemand! rdim=2 cdim=1
$offecho
$call GDXXRW C:\Users\david\GitHub\aperc-osemosys\data\master-data-UTOPIA.xlsx @task2.txt ignoreColumns=C,D trace=4
$gdxin master-data-UTOPIA.gdx
$load AccumulatedAnnualDemand
$gdxin


