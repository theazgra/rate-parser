# -*- coding: utf-8 -*-
import collections
import sys
from shutil import copy2
import os
import re

def main():
    arguments = sys.argv
    if len(arguments) != 5:
        print('\n**Napoveda**')
        print('\nSkript potrebuje 4 parametry. [1] TTD soubor, [2] slozku s textovymi soubory, [3] textovy soubor s jednotnymi kurzy nebo None, [4] rok')
        print('\nPokud chcete zadat jednotne kurzy rucne, zadejte jako parametr None. Textovy soubor je vytvoren zkopirovanim tabulky z pdf, tudiz mezi hodnotami jsou jen mezery')
        print('\nPriklad spousteni skriptu: py KurzParser_v2 ttdSoubor.ttd slozka YK.txt 2016')
        return False
    TTD_file = arguments[1]
    txt_files_folder = arguments[2]
    YK_file = arguments[3]
    YEAR = arguments[4]
    #################################
    #Zde zadejte rucne jednotne kurzy ponechejte je jako string
    #################################
    if YK_file.upper() == 'NONE':
        print('\nPouziti jednotnych kurzu ze skriptu.')
        YK_dict = {
            'Austrálie' : '18.22',
            'Brazílie'  : '7.13',
            'Bulharsko'  : '13.83',
            'Čína'  : '3.69',
            'Dánsko'  : '3.63',
            'EMU'  : '27.04',
            'Filipíny'  : '51.48',
            'Hongkong'  : '3.16',
            'Chorvatsko'  : '3.59',
            'Indie'  : '36.46',
            'Indonesie'  : '1.84',
            'Izrael'  : '6.40',
            'Japonsko'  : '22.50',
            'Jihoafrická rep.'  : '1.68',
            'Jižní Korea'  : '2.11',
            'Kanada'  : '18.54',
            'Maďarsko'  : '8.67',
            'Malajsie'  : '5.92',
            'Mexiko'  : '1.31',
            'MMF'  : '34.01',
            'Norsko'  : '2.92',
            'Nový Zéland'  : '17.11',
            'Polsko'  : '6.18',
            'Rumunsko'  : '6.02',
            'Rusko'  : '37.07',
            'Singapur'  : '17.74',
            'Švédsko'  : '2.86',
            'Švýcarsko'  : '24.79',
            'Thajsko'  : '69.60',
            'Turecko'  : '8.11',
            'USA'  : '24.53',
            'Velká Británie'  : '32.96',
        }
    else:
        try:
            with open(YK_file) as file:
                YK_content = file.readlines()
        except FileNotFoundError as e:
            print(e)

        two_word_countries = (
            'Jihoafrická',
            'Jižní',
            'Nový',
            'Velká'
        )

        YK_dict = {}
        for line in YK_content:
            tmp = line.rstrip().split(' ')
            #Osetrni statu s dvouslovnym nazvem
            if tmp[0] in two_word_countries:
                YK_dict[tmp[0]+' '+tmp[1]] = tmp[5].replace(',', '.')
            #Osetreni u rumunska nebot ma dvouslovnou menu
            elif tmp[0] == 'Rumunsko':
                YK_dict[tmp[0]] = tmp[5].replace(',', '.')
            else:
                YK_dict[tmp[0]] = tmp[4].replace(',', '.')

        if len(YK_dict) != 32:
            print('V textovem souboru jednotnych kurzu nebyli nalezeny vsechny staty.')
            quit()


    #Vytvoreni zalohy TTD souboru
    print('\nVytvoreni zalohy originalniho TTD souboru')
    copy2(TTD_file, TTD_file[:len(TTD_file)-4] + '_zaloha.TTD ')

    #Nalezeni ID posledniho zaznamu v TTD souboru
    try:
        with open(TTD_file, 'r', encoding="utf-8") as fh:
            last_line = fh.readlines()
            fh.close()
            last_line = str(last_line[len(last_line)-1:]).rstrip()
    except FileNotFoundError as e:
        print(e)
    #pokud je TTD soubor prazdny nastavi prvni index na 0
    if last_line[2:last_line.find('\\t')] == '':
        last_line_index = 0
    else:
        last_line_index = int(last_line[2:last_line.find('\\t')]) + 1

    #Kontrola textovych souboru v zadane slozce, musi odpovidat formatu DD_MM_YYYY
    pattern = '[0-3]{1}[0-9]{1}[_]{1}[0-1]{1}[0-9]{1}[_]{1}\d{4}[.txt]{1}'
    ignored_files = 0
    files_by_month = {}
    for file in os.listdir(txt_files_folder):
        if re.match(pattern, file):
            if not int(file[file.find('_')+1:5]) > 12:
                files_by_month[int(file[file.find('_')+1:5])] = file
            else:
                print('\nSoubor ' + file + ' neni ve spravnem formatu. Existuje pouze 12 mesicu!')
                ignored_files += 1
        else:
            print('\nSoubor ' + file + ' neodpovida formatu DD_MM_RRRR.txt. Priklad: 11_11_2016.txt')
            ignored_files += 1

    print('\nCelkem nacteno ' + str(len(files_by_month)) + ' textovych souboru/y. ' + str(ignored_files) + ' soubor/y v nespravnem formatu.')

    choice = input('\nPokracovat? ''A'' ano, ''N'' ne: ')
    if choice.upper() == 'A':
        iteration = 0
        for f in files_by_month:
            print('Nacitani ' + files_by_month[f])
            file_content = []
            #Vytvoreni data z nazvu souboru
            DATE = files_by_month[f][:files_by_month[f].find('.txt')].replace('_','.')

            try:
                with open(txt_files_folder + '/' + files_by_month[f],'r',encoding="utf-8") as work_file:
                    file_content = work_file.readlines()
            except FileNotFoundError as e:
                print(e)
            #Smazani hlavnicky textoveho souboru
            del file_content[0]
            del file_content[0]

            index = 0
            parsedContent = []
            for index in range(0,len(file_content)):
                #Rozsekani radku na stat, mnozstvi, menu a kurz
                tmp = file_content[index].split('|')
                #zapsani hodnot do listu
                parsedContent.append([str(int(last_line_index)+index+iteration), tmp[0].strip(),tmp[3].strip(), tmp[2].strip(), DATE, tmp[4].strip().replace(',','.'), YK_dict[tmp[0].strip()], YEAR])


            try:
                print('Zapisovani do souboru ' + TTD_file)
                TTD_file_to_write = open(TTD_file ,'a', encoding="utf-8")
                for line in parsedContent:
                    TTD_file_to_write.write('\n' + str(line[0] +'\t' + line[1] + '\t' + line[2] + '\t' + line[3] + '\t' + line[4] + '\t' + line[5] + '\t' + line[6] + '\t' + line[7]))
                        #zapsani do zvoleneho TTD souboru

            except FileNotFoundError as e:
                print(e)

            iteration += len(file_content)

        TTD_file_to_write.close()
    else:
        print('\nUkonceni skriptu.')
        quit()


if __name__ == "__main__":
    main()
