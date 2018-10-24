import argparse
import main


if __name__ == '__main__':

   parser = argparse.ArgumentParser()

   # Parse input arguments
   parser.add_argument('game_type',choices=['o','m'],type=str, help = 'game type - o:original wisconsin game, m:modified wisconsin game')
   parser.add_argument('user_id',type=int, help = 'player id')
   parser.add_argument('--modality',default='v',type=str,choices=['v','a','t'] ,help = 'stimuli type - v:visual, t:text, a:audio')
   parser.add_argument('--store_data',default='../../Wisconsin_Unimodal_Data/',type=str, help = 'path to store the data')


   args = parser.parse_args()
   main.main(args.game_type,str(args.user_id),args.modality,args.store_data)
