def center(text, space_from_edges): 
	third_line = '##'
	for _ in range(space_from_edges):
		third_line += ' '
	third_line += text 
	for _ in range(space_from_edges):
		third_line += ' '
	third_line += '##\n'
	frame_len = len(third_line) -1
	first_line = ''
	fifth_line = ''
	for _ in range(frame_len):
		first_line += '#'
		fifth_line += '#'
	first_line +='\n'
	fifth_line += '\n\n\n'
	second_line = '##'
	for _ in range(frame_len - 4):
		second_line += ' '
	second_line += '##\n'
	fourth_line = second_line
	complete_text = first_line + second_line + third_line + fourth_line + fifth_line
	return complete_text
	

