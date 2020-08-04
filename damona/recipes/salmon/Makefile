
salmon_1.3.0:
	sudo singularity build salmon.img Singularity.salmon_1.3.0

push:
	singularity sign salmon.img
	singularity push salmon.img library://cokelaer/damona/salmon:1.3.0
