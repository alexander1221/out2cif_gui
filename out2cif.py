import mmap
import os
import re
import sys
import time
from os import listdir
from os.path import isfile, join

from dict_sym_ops import *

def update_progress(i, total, length=20, fg="#", bg=" ", decimals=0):
    progress = 100 * (i / float(total))
    blocks = int(length * i // total)
    bar = fg * blocks + bg * (length - blocks)
    sys.stderr.write(f"\r[{bar}] {progress:.{decimals}f}%")
    sys.stderr.flush()


def O2C(f, pathsave):
    with open(f, 'r+') as fre:
        data = mmap.mmap(fre.fileno(), 0)
        # mo = re.search(b'(CRYSTAL)\n(\d \d \d)\n(.*)', data)
        mo_str = re.search(b'(SPACE GROUP)(.*)', data)
        # print(mo_str.group().decode('ascii').split(':')[1].replace(' ', ''))
        if mo_str:
            spg_find = mo_str.group().decode('ascii').split(':')[1].replace(' ', '')
            print('spg_find = ' + spg_find)

    for key, value in HM2Hall.items():
        if  spg_find.casefold().strip() == key.casefold():
            print('Hall name of spg find is ' + value)
            spg_HM = key
            sg_name_Hall = value

    sg_number = Hall2Number[sg_name_Hall]

    if sg_number in range(1, 3):
        cell_set = 'triclinic'
    elif sg_number in range(3, 16):
        cell_set = 'monoclinic'
    elif sg_number in range(16, 75):
        cell_set = 'orthorombic'
    elif sg_number in range(75, 143):
        cell_set = 'tetragonal'
    elif sg_number in range(143, 168):
        cell_set = 'trigonal'
    elif sg_number in range(168, 195):
        cell_set = 'hexagonal'
    elif sg_number in range(195, 231):
        cell_set = 'cubic'

    print(sg_number)
    print(cell_set)

    sg_ops = SymOpsHall[sg_name_Hall]

    sym_ops_str = ''
    ops_count = 0
    for x in sg_ops:
        ops_count += 1
        x = ",".join([i.strip() for i in x])
        sym_ops_str += str(ops_count) + ' ' + x + '\n'


    print(sym_ops_str)

    string2find_start = "FINAL OPTIMIZED GEOMETRY"
    string2find_end = "TOTAL CPU TIME"

    str_id = f[:-4]
    str_id = str_id.split(sep='/')[-1]
    counter = 0
    a_list = []
    counter = 0

    with open(f, "rt") as crystal_out:
        for myline in crystal_out:
            if myline.find(string2find_start) == 1:
                counter += 1
            if counter > 0:
                a_list.append(myline)
            if myline.find(string2find_end) == 4:
                break
    crystal_out.close()

    fobj = open(f"{pathsave}/fog.txt", 'w')  # We create file object to write data into output file
    for h in range(0, len(a_list)):
        fobj.write('{}'.format(a_list[h]))
    fobj.close()  # Closes file object

    fo = open(f"{pathsave}/fog.txt", 'r')  # Open input file in order to read it
    b_list = fo.readlines()  # Read files line by line and write it in list, where every line is presented as single element of the list
    fo.close()  # We need to close f because we do not need it any more (because we have digiyal copy of it) and now it just wastes our memory

    index_cut = b_list.index(' T = ATOM BELONGING TO THE ASYMMETRIC UNIT\n')
    b_list = b_list[:index_cut - 1]
    # print(b_list)
    # print(b_list[70:71])

    if any("COORDINATES IN THE CRYSTALLOGRAPHIC CELL" in s for s in b_list):
        index_prim_tab = b_list.index(' TRANSFORMATION MATRIX PRIMITIVE-CRYSTALLOGRAPHIC CELL\n')
        primitive_cell_params = b_list[6].split()
        primitive_cell_a = primitive_cell_params[0]
        primitive_cell_b = primitive_cell_params[1]
        primitive_cell_c = primitive_cell_params[2]
        primitive_cell_alpha = primitive_cell_params[3]
        primitive_cell_beta = primitive_cell_params[4]
        primitive_cell_gamma = primitive_cell_params[5]
        primitive_cell_params_vol = b_list[4].split()[7]
        primitive_cell_tab = b_list[11:index_prim_tab - 1]

        print(primitive_cell_params)
        print(primitive_cell_params_vol)
        # print(primitive_cell_tab)

        cell_vol = b_list[index_prim_tab + 4].split()[3][:-1]
        cryst_cell_params = b_list[index_prim_tab + 6].split()
        cell_a = cryst_cell_params[0]
        cell_b = cryst_cell_params[1]
        cell_c = cryst_cell_params[2]
        cell_alpha = cryst_cell_params[3]
        cell_beta = cryst_cell_params[4]
        cell_gamma = cryst_cell_params[5]
        cell_tab = b_list[index_prim_tab + 11:]

        print(cryst_cell_params)
        print(cell_vol)
        # print(cryst_cell_tab)
        list_of_atoms = cell_tab
    else:
        primitive_cell_params = b_list[6].split()
        cell_a = primitive_cell_params[0]
        cell_b = primitive_cell_params[1]
        cell_c = primitive_cell_params[2]
        cell_alpha = primitive_cell_params[3]
        cell_beta = primitive_cell_params[4]
        cell_gamma = primitive_cell_params[5]
        cell_vol = b_list[4].split()[7]
        cell_tab = b_list[11:index_cut - 1]

        print(primitive_cell_params)
        print(cell_vol)
        # print(primitive_cell_tab)
        list_of_atoms = cell_tab

    true_atoms = []

    ato = [i.split(" ") for i in list_of_atoms]
    atoms = [' '.join(i).split() for i in ato]
    # print(list_of_atoms)

    for x in atoms:
        if x[1] == 'T':
            true_atoms.append(x)



    for x in true_atoms:
        del x[0]
        del x[1]

    print('  ', '  ')

    element_counter = [['Em', 0], ['Vc', 0], ['Va', 0], ['H', 0], ['D', 0], ['HE', 0], ['LI', 0], ['BE', 0], ['B', 0],
                       ['C', 0], ['N', 0], ['O', 0], ['F', 0], ['NE', 0], ['NA', 0], ['MG', 0], ['AL', 0], ['SI', 0],
                       ['P', 0], ['S', 0], ['CL', 0], ['AR', 0], ['K', 0], ['CA', 0], ['SC', 0], ['TI', 0], ['V', 0],
                       ['CR', 0], ['MN', 0], ['FE', 0], ['CO', 0], ['NI', 0], ['CU', 0], ['ZN', 0], ['GA', 0],
                       ['GE', 0],
                       ['AS', 0], ['SE', 0], ['BR', 0], ['KR', 0], ['RB', 0], ['SR', 0], ['Y', 0], ['ZR', 0], ['NB', 0],
                       ['MO', 0], ['TC', 0], ['RU', 0], ['RH', 0], ['PD', 0], ['AG', 0], ['CD', 0], ['IN', 0],
                       ['SN', 0],
                       ['SB', 0], ['TE', 0], ['I', 0], ['XE', 0], ['CS', 0], ['BA', 0], ['LA', 0], ['CE', 0], ['PR', 0],
                       ['ND', 0], ['PM', 0], ['SM', 0], ['EU', 0], ['GD', 0], ['TB', 0], ['DY', 0], ['HO', 0],
                       ['ER', 0],
                       ['TM', 0], ['YB', 0], ['LU', 0], ['HF', 0], ['TA', 0], ['W', 0], ['RE', 0], ['OS', 0], ['IR', 0],
                       ['PT', 0], ['AU', 0], ['HG', 0], ['TL', 0], ['PB', 0], ['BI', 0], ['PO', 0], ['AT', 0],
                       ['RN', 0],
                       ['FR', 0], ['RA', 0], ['AC', 0], ['TH', 0], ['PA', 0], ['U', 0], ['NP', 0], ['PU', 0], ['AM', 0],
                       ['CM', 0], ['BK', 0], ['CF', 0], ['ES', 0], ['FM', 0], ['ME', 0], ['NO', 0], ['LR', 0],
                       ['RF', 0],
                       ['DB', 0], ['SG', 0], ['BH', 0], ['HS', 0], ['MT', 0]]
    el_count = element_counter.copy()

    for x in true_atoms:
        for z in el_count:
            if x[1] == z[0]:
                z[1] += 1
                x[0] = z[0] + str(z[1])

    true_atom_table = ''
    for x in true_atoms:
        x = " ".join([i.strip() for i in x])
        true_atom_table += x + '\n'

    intro = '''#######################################################################''' + '\n' + '#' + '\n' + '#                 Cambridge Crystallographic Data Centre' + '\n' + '#                                CCDC ' + '\n' + '''#######################################################################''' + '\n' + '#' + '\n' + '# If this CIF has been generated from an entry in the Cambridge ' + '\n' + '# Structural Database, then it will include bibliographic, chemical, ' + '\n' + '# crystal, experimental, refinement or atomic coordinate data resulting' + '\n' + '# from the CCDC\'s data processing and validation procedures.' + '\n' + '''#######################################################################''' + '\n' + '#' + '\n' + ''

    data_cryst = 'data_' + str_id + '\n' + '_symmetry_cell_setting           ' + cell_set + '\n' + '_symmetry_space_group_name_H-M   ' + spg_HM + '\n' + '_symmetry_Int_Tables_number      ' + str(sg_number) + '\n' + '_space_group_name_Hall           ' + sg_name_Hall + '\n' + 'loop_' + '\n' + '_symmetry_equiv_pos_site_id' + '\n' + '_symmetry_equiv_pos_as_xyz' + '\n' + sym_ops_str + '_cell_length_a                   ' + cell_a + '\n' + '_cell_length_b                   ' + cell_b + '\n' + '_cell_length_c                   ' + cell_c + '\n' + '_cell_angle_alpha                ' + cell_alpha + '\n' + '_cell_angle_beta                 ' + cell_beta + '\n' + '_cell_angle_gamma                ' + cell_gamma + '\n' + '_cell_volume                     ' + cell_vol + '\n' + 'loop_' + '\n' + '_atom_site_label' + '\n' + '_atom_site_type_symbol' + '\n' + '_atom_site_fract_x' + '\n' + '_atom_site_fract_y' + '\n' + '_atom_site_fract_z' + '\n'

    print(pathsave)
    print(str_id)
    fi = open(f"{pathsave}/{str_id}.cif", 'w')
    fi.write(intro)
    fi.write(data_cryst)
    fi.write(true_atom_table)
    fi.write('\n' + '#END')
    fi.close()

    os.remove("fog.txt")

dir_path = os.getcwd() #os.path.dirname(os.path.realpath(__file__))

onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]


def main(path_list, path2save):
    files_toprocess = set()
    paths = path_list
    print(paths)
    for p in paths:
        if os.path.isfile(p) and p.endswith('.out'):
            files_toprocess.add(p)
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                files_toprocess.update([os.path.join(root, f) for f in files if f.endswith('.out')])
    file_counter = 0


    for i in files_toprocess:
        file_counter+=1
        try:
            print(i)
            O2C(i, path2save)
            time.sleep(0.021)
            update_progress(file_counter, len(files_toprocess))
        except:
            continue
    return file_counter


if __name__ == "__main__":
    main()
    time.sleep(5)