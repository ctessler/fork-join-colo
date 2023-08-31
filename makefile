all:
	$(MAKE) -C ./simul/ clean					# Remove Previous RISCV Experiment
	$(MAKE) -f gen.mk group-e -C ./eval/				# Generate Group E
	$(MAKE) -f gen.mk group-x -C ./eval/				# Generate Group X
	$(MAKE) -C ./simul/ all						# Run RISCV Experiment
	./simul/export.sh artifacts $(shell pwd) $@			# Export RISCV Experiment Data
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export GroupE/GroupX Data
	cp graph-tmplt.tex ./$@/graph.tex				# Copy Graph Template for PDF Generation
	sed -i -e '71 e cat ./$@/mrtc-base-incr.tex' ./$@/graph.tex     # Replace Template with RISCV Sim Data
	sed -i -e s/target/$@/g ./$@/graph.tex	 			# Replace Target Directory
	cd ./$@ && latexmk -pdf graph.tex && latexmk -c			# PDF Generation	
	mv ./$@/graph.pdf ./$@/result-summary.pdf			# Rename File to Result-Sumary
	open $@/result-summary.pdf					# Open pdf
	nautilus $@							# Open Directory

verify: 
	$(MAKE) -C ./simul/ clean					# Remove Previous RISCV Experiment
	$(MAKE) -C ./simul/ all						# Run RISCV Experiment
	./simul/export.sh artifacts $(shell pwd) $@			# Export RISCV Experiment Data
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export GroupE/GroupX Data
	cp graph-tmplt.tex ./$@/graph.tex				# Copy Graph Template for PDF Generation
	sed -i -e '71 e cat ./$@/mrtc-base-incr.tex' ./$@/graph.tex     # Replace Template with RISCV Sim Data
	sed -i -e s/target/$@/g ./$@/graph.tex	 			# Replace Target Directory
	cd ./$@ && latexmk -pdf graph.tex && latexmk -c			# PDF Generation	
	mv ./$@/graph.pdf ./$@/result-summary.pdf			# Rename File to Result-Sumary
	open $@/result-summary.pdf					# Open pdf
	nautilus $@							# Open Directory

quick: 
	$(MAKE) -C ./simul/ clean					# Remove Previous RISCV Experiment
	$(MAKE) -f gen.mk tiny -C ./eval/				# Generate Group Tiny
	$(MAKE) -C ./simul/ all						# Run RISCV Experiment
	./simul/export.sh artifacts $(shell pwd) $@ 			# Export RISCV Experiment Data
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export GroupE/GroupX Data
	cp graph-tmplt.tex ./$@/graph.tex				# Copy Graph Template for PDF Generation
	sed -i -e '71 e cat ./$@/mrtc-base-incr.tex' ./$@/graph.tex     # Replace Template with RISCV Sim Data
	sed -i -e s/target/$@/g ./$@/graph.tex				# Replace Target Directory
	cd ./$@ && latexmk -pdf graph.tex && latexmk -c			# PDF Generation	
	mv ./$@/graph.pdf ./$@/result-summary.pdf			# Rename File to Result-Sumary
	open $@/result-summary.pdf					# Open pdf
	nautilus $@							# Open Directory
	
	
simulation_tiny: 
	$(MAKE) -f gen.mk tiny -C ./eval/				# Generate Group Tiny
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export Provided Data
	nautilus $@

simulation_small: 
	$(MAKE) -f gen.mk small -C ./eval/				# Generate Group Small
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export Provided Data
	nautilus $@							# Open Directory

	
simulation_set_e: 
	$(MAKE) -f gen.mk group-e -C ./eval/				# Generate Group X
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export Provided Data
	nautilus $@							# Open Directory

simulation_set_x:
	$(MAKE) -f gen.mk group-x -C ./eval/
	./eval/export.sh artifacts $(shell pwd) $@ 			# Export Provided Data
	nautilus $@


riscv-experiment:
	$(MAKE) -C ./simul/ clean					# Remove Previous RISCV Experiment
	$(MAKE) -C ./simul/ all						# Run RISCV Experiment
	./simul/export.sh artifacts $(shell pwd) $@
	nautilus $@
	
clean:
	rm -rf riscv-experiment
	rm -rf simulation_set_x
	rm -rf simulation_set_e
	rm -rf simulation_small
	rm -rf simulation_tiny
	rm -rf quick
	rm -rf verify
	rm -rf all
	