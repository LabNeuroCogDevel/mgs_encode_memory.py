image_list.txt:
	cd img;\
	find A B -type f > ../image_list.txt

img/overview/in_A.pdf: img/overview/generate.bash
	img/overview/generate.bash
