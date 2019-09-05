# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:57:06 2019

@author: Byron_Adrian_Gmn
"""


# -*- coding: utf-8 -*-

# author: vlarobbyk
# Catedra UNESCO Tecnologías de apoyo para la Inclusión Educativa 
# Grupo de Investigación en Inteligencia Artificial y Tecnologías de Asistencia (GI-IATa)
from collections import OrderedDict
from nltk.corpus import stopwords
from pattern.es import conjugate
import collections
import random
import copy  
import spacy
import heapq
import nltk
import re


class QAGenerator:
    
    def __init__(self):
        self.nlp = spacy.load('es')
        
        self.rlv_taggs = ['ADJ','ADV','NOUN','PRON','VERB','PROPN']
        self.dias = ['lunes','martes','miercoles','jueves','viernes','sabado', 'domingo'] 
        self.meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
        self.lugares = ['bosque', 'habitacion', 'casa', 'escuela', 'tienda', 'cueva', 'castillo', 'alcoba']
        self.personajes=[]
    
    def who_answer(self,sentence):
        verbo_root=None
        tokens = [token for token in sentence]       
        for token in tokens:
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                verbo_root = token
                #print('\nVerbo Principal [',token,']')    
        persi=['cortes','hombre']
        for token in tokens:
           if token.dep_ == 'nsubj' and token.pos_ == 'NOUN' and token.head.text == verbo_root.text and token.text not in persi:
               #print('Personaje relacionado con [', verbo_root, '] es: [', token.text.upper(),']')
               return token.text
        return None   
    

    def to_conjugate(self,verbo):
        mod = ['INDICATIVE', 'IMPERATIVE', 'CONDITIONAL', 'SUBJUNCTIVE']
        aspec = ['IMPERFECTIVE', 'PERFECTIVE', 'PROGRESSIVE']
        tiempo = ['INFINITIVE', 'PRESENT', 'PAST', 'FUTURE']
        tiempo = tiempo[2]
        PALABRA = verbo
        PERSONA = 3
        cong = conjugate(PALABRA,tense = tiempo.lower(),# INFINITIVE, PRESENT, PAST, FUTURE 
                    person = PERSONA,                   # 1, 2, 3 or None 
                    number = 'SG'.lower(),              # SG, PL 
                    mood = mod[0].lower(),              # INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE 
                    aspect = aspec[1].lower(),          # IMPERFECTIVE, PERFECTIVE, PROGRESSIVE 
                    negated = False)
        return cong
    
    def pronoun_se(self,oracion,texto):
        oracion=self.nlp(str(oracion))
        pronombre=None      
        for token in oracion:
            if token.text == texto:   
                ant_token = oracion[token.i-1]
                if ant_token.text.lower() == 'se' or ant_token.text.lower() == 'no':
                    pronombre=str(ant_token)

                break
        return pronombre
    
    def pronoun(self,oracion,texto):
        oracion=self.nlp(str(oracion))
        pronombre=None
        
        for token in oracion:
            if token.text == texto:   
                ant_token = oracion[token.i-1]
                if ant_token.dep_=='det' and ant_token.pos_== 'DET':
                    pronombre=str(ant_token)
                    return pronombre
                break
        return None
    
    
    def where_question(self,sentence, tokens, i, rlv_words, ents1):
        oracion, donde, respuesta='','¿A dónde ',''
        oracion += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:]])
        donde += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[i:i+1]])
        respuesta += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:i]])+'?'
        doc=self.nlp(respuesta)
        doc=[tok.text for tok in doc]
        pers=self.who_answer(sentence)
        
        if pers == None:
            for r in rlv_words:
                if r[0] in doc:
                    pers=r[0] 
        
        if pers != None:
            pron=self.pronoun(sentence,pers)
            if pron != None:
                donde=donde+' '+pron+' '+pers+'?'
            else:
                donde=donde+' '+pers+'?'
            
            opciones = self.lugares            
            
            for l,t in ents1:
                if t != pers:
                    respuesta = t
                    try:
                        opciones.remove(respuesta.lower())
                    except ValueError:
                        opciones=opciones            
                    opcion1=random.choice(opciones)            
                    try:
                        opciones.remove(opcion1.lower())
                    except ValueError:
                        opciones=opciones
                    opcion2=random.choice(opciones)           
                    return oracion,donde,respuesta.lower(), opcion1,opcion2
        return None
    
    def when_question(self,sentence, tokens, tokens1, i, rlv_words, ents1):
        oracion, cuando, respuesta='','',''
        oracion += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:]])
        cuando += ' '.join([ (tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[i:i+1]])
        
        respuesta += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:i]])+'?'
        doc=self.nlp(respuesta)
        doc=[tok.text for tok in doc]
        pers=self.who_answer(sentence)
        
        if pers == None:
            for r in rlv_words:
                if r[0] in doc:
                    pers=r[0] 
        pron=self.pronoun(sentence,pers)
        if pron != None:
            cuando=cuando+' '+pron+' '+pers+'?'
        else:
            cuando=cuando+' '+pers+'?'            

        
        if len([i for i in self.dias if i in tokens1]) == 1:
            cuando = '¿Qué día '+cuando
            respuesta=str([i for i in self.dias if i in tokens1][0])
            opciones = self.dias            
            try:
                opciones.remove(respuesta.lower())
            except ValueError:
                opciones=opciones            
            opcion1=random.choice(opciones)            
            try:
                opciones.remove(opcion1.lower())
            except ValueError:
                opciones=opciones
            opcion2=random.choice(opciones)  
            return oracion,cuando,respuesta.lower(), opcion1, opcion2
        
        elif len([i for i in self.meses if i in tokens1]) == 1:
            cuando = '¿Qué mes '+cuando
            respuesta= str([i for i in self.meses if i in tokens1][0])
            opciones = self.meses            
            try:
                opciones.remove(respuesta.lower())
            except ValueError:
                opciones=opciones            
            opcion1=random.choice(opciones)            
            try:
                opciones.remove(opcion1.lower())
            except ValueError:
                opciones=opciones
            opcion2=random.choice(opciones)   
            return oracion,cuando,respuesta.lower(), opcion1, opcion2
        return None
    
    def who_question(self, sentence, token, tokens, i, rlv_words):
        tags = token.tag_.split('|') 
        
        oracion, quien, respuesta='','¿Quién ',''
        if 'Number=Sing' in tags and 'Person=3' in tags and 'VERB__Mood=Ind' in tags and 'Tense=Past' in tags:
            token = token
        else:
            token = self.to_conjugate(token.lemma_)                    
        oracion += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:]])                    
        pron=self.pronoun_se(sentence,str(token))
        
        if pron != None:
            quien =quien+pron+' '+str(token)+' '
        else:        
            quien =quien+str(token)+' '                        
        quien += ' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[i+1:]])+'?'
        quien=quien.strip().strip().strip().strip().strip()   
        respuesta +=' '.join([(tok.pos_ != 'SPACE' and (tok.text) or ("") ) for tok in tokens[:i]])                      
        


        doc=self.nlp(respuesta)
        doc=[tok.text for tok in doc]               
        respuesta=self.who_answer(sentence)



        quien_nlp=self.nlp(quien)
        quien_nlp=[tok.text for tok in quien_nlp] 

        opciones = copy.copy(self.personajes)
        


        if respuesta != None and respuesta not in quien_nlp:

            num = self.nlp(respuesta)
            num=num[0].tag_.split('|')
            if 'Number=Plur' not in num:

                respuesta=str(respuesta).capitalize()
                try:
                    opciones.remove(respuesta)
                except ValueError:
                    opciones=opciones            
                opcion1=random.choice(opciones)  
                
                try:
                    opciones.remove(opcion1)
                except ValueError:
                    opciones=opciones
                opcion2=random.choice(opciones)
                opciones.remove(opcion2)
                return oracion,quien,respuesta,opcion1,opcion2
        else:
            for r in rlv_words:
                
                if r[0] in doc:
                    respuesta=str(r[0]).capitalize()
                    try:
                        opciones.remove(respuesta)
                    except ValueError:
                        opciones=opciones            
                    opcion1=random.choice(opciones)  
                    
                    try:
                        opciones.remove(opcion1)
                    except ValueError:
                        opciones=opciones
                    opcion2=random.choice(opciones)
                    opciones.remove(opcion2) 
                    return oracion,quien,respuesta,opcion1,opcion2
        return None
    
    def who_options(self,text):
        doc = self.nlp(text)
        pers = []
        for sentence in doc.sents:
            tokens = [token for token in sentence]     
            for token in tokens:
                if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                    if self.who_answer(sentence) != None :
                        pers.append(str(self.who_answer(sentence)).capitalize())
            
        remover = ['Gorro','Habitación', 'Suerte','–','Amenazó','–"hijos','Saco','Cortes']
        for rem in remover:
            try:
                pers.remove(rem)  
            except ValueError:
                pers=pers    
        pers=list(OrderedDict.fromkeys(pers))
        
        #print(pers)
        return pers
    
    def make_question(self, sentence, rlv_words):
        
        tokens = [token for token in sentence]     
        i = 0
        for token in tokens:
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                ents1 = [(e.label_,e.text) for e in sentence.ents]
                ents = [(e.label_) for e in sentence.ents]
                
                if 'LOC' in ents: 
                    Resultado = self.where_question( sentence, tokens, i, rlv_words, ents1)
                    if (Resultado)!= None:
                        return Resultado[0],Resultado[1],Resultado[2],Resultado[3],Resultado[4]                          
                        
                tokens1 = [token.text.lower() for token in sentence]
                if ('DATE' in ents) or ([i for i in self.dias if i in tokens1]) or ([i for i in self.meses if i in tokens1]):                   
                    Resultado = self.when_question( sentence, tokens, tokens1, i, rlv_words, ents1)
                    if (Resultado)!= None:
                        return Resultado[0],Resultado[1],Resultado[2],Resultado[3],Resultado[4]                      
 
                else: 
                    Resultado = self.who_question(  sentence, token, tokens, i, rlv_words)
                    if (Resultado)!= None:
                        return Resultado[0],Resultado[1],Resultado[2],Resultado[3],Resultado[4]                      
            i+=1
        return None
                
    def process(self,Titulo,Texto):
        
        key_sentences,key_sentences_copy = [],[]
        other_sentences,other_sentences_copy = [],[]
        #Carga, Titulo
        rlv_title = self.get_most_relevant(Titulo)
        #Carga, Texto
        doc = self.nlp(Texto)
        tempx = []
        
        for sentence in list(doc.sents):                
            if str(sentence).find('"') == -1:    
                for elem in rlv_title:
                    tempx = [token.string for token in sentence]                    
                    if elem[len(elem)-1].search(' '.join(tempx)):                       
                        if sentence not in key_sentences:
                            key_sentences.append(sentence)
                            
                            oracion = self.nlp(str(sentence).strip('\n').strip(" "))
                            key_sentences_copy.append(oracion)
                        elif sentence not in other_sentences:
                            other_sentences.append(sentence)
                            
                            oracion = self.nlp(str(sentence))
                            other_sentences_copy.append(oracion)      
        return (key_sentences_copy, other_sentences_copy)
        
    def get_most_relevant(self, text):
        text= text+' '+text.lower()
        tmp = self.nlp(text)
        rlv = []
        for token in tmp:
            #print(token.text, token.pos_)
            if token.pos_ in self.rlv_taggs:
                rlv.append((token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop, re.compile('('+token.text.lstrip().rstrip()+')')))
        
        return rlv
    
    def nltk_summarizer(self, raw_text, n_oraciones):
        
        
        stopWords = set(stopwords.words("spanish"))
        word_frequencies = {}  
        for word in nltk.word_tokenize(raw_text):  
            if word not in stopWords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1    
        maximum_frequncy = max(word_frequencies.values())    
        for word in word_frequencies.keys():  
            word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)    
        sentence_list = nltk.sent_tokenize(raw_text)
        sentence_scores = {}  
        for sent in sentence_list:  
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]    
        summary_sentences = heapq.nlargest(n_oraciones, sentence_scores, key=sentence_scores.get)    
        oraciones={}
        for sent in summary_sentences:
            if sent in summary_sentences:
                cont=0
                for doxsent in sentence_list:
                    if str(doxsent) == str(sent):
                        oraciones.update({cont:sent})    
                    cont=cont+1
        oraciones = collections.OrderedDict(sorted(oraciones.items()))
        summary_sentences = []
        for k, v in oraciones.items():
            if str(v).find('"') == -1:   
                oracion = self.nlp(v)
                summary_sentences.append(oracion)    
        #summary = ' '.join(summary_sentences)  
        return summary_sentences

    def make_simple_questions(self,Titulo, Texto):
        
        try:  
            self.to_conjugate('ir')
        except:
            pass
        
        # Carga Titulo, Texto
        key_sentences, other_sentences = self.process(Titulo, Texto)
#        print(key_sentences, other_sentences)
        question = None

        
        #Carga, Texto
        summarize = self.nltk_summarizer(Texto,15)
        #Carga, Titulo
        rlv_words = self.get_most_relevant(Titulo)
        

        #Unimos las oraciones del resumen + 
        #las oraciones con palabras relevantes
        presente = False
        for sentence in summarize:
            presente = False
            for sent in key_sentences:
                if str(sent) == str(sentence):
                    presente=True
            if presente == False:
                key_sentences.append(sentence)
                
        #print('\nOraciones:\n',key_sentences,'\n',)
        #Carga, Texto
        self.personajes=self.who_options(Texto)
        Respuesta=[]
        Num_Preguntas=0
        for sentence in key_sentences:
            question =  self.make_question(sentence, rlv_words)
            if Num_Preguntas < 10:
                if question != None:
                    #print('\nPregunta generada: \n-%s \n-%s [%s] [%s]' % (question[1],question[2],question[3],question[4]))
                    Respuesta.append(question[1])
                    Respuesta.append(question[2])
                    Respuesta.append(question[3])
                    Respuesta.append(question[4])
                    Num_Preguntas=int(len(Respuesta)/4)
        
        return Respuesta
        
if __name__=="__main__":
    qagenerator = QAGenerator()
    #Enano Saltarin
    # example_text1 = (u'Hace mucho tiempo, existió un rey que gustaba de dar largos paseos por el bosque. Un buen día, y cansado de tanto cabalgar, el monarca llegó a una humilde casita entre los árboles. En aquel lugar, vivía un agricultor con su hija joven, la cual rápidamente se ganó la admiración del rey por su belleza. "Mi hija no solo es bella, sino que también tiene un don especial" – alardeaba el campesino. Cuando el rey le preguntó de qué se trataba, el anciano respondió que la muchacha era capaz de convertir en oro la paja seca con el uso de una rueca. "Genial, la llevaré conmigo al palacio" – gritó entonces el rey. Al llegar al enorme castillo, el monarca condujo a la joven doncella hacia una habitación donde se encontraba una rueca rodeada de paja. "A la mañana siguiente vendré a ver si es verdad que puedes convertir todo esto en oro. Si me engañas, tú y tu padre sufrirán las consecuencias por haberme mentido". Al no saber qué hacer, la pobre muchacha se desplomó en el suelo y se puso a llorar hasta la llegada de la noche. Entonces, cuando dieron exactamente las doce en el reloj, apareció por una de las ventanas, un enano narizón que prometió ayudarla. "Si me regalas tu collar, convertiré toda esta paja en oro" – dijo el enano con una voz suave, y sin pensarlo dos veces, la hermosa joven le entregó su collar a la criatura, y esta se dispuso a hilar la rueca con toda la paja de la habitación. A la mañana siguiente, el rey abrió la puerta y quedó boquiabierto de ver que, efectivamente, toda la paja había sido convertida en oro. Cegado por su ambición, el rey tomó a la muchacha por las manos y la llevó hacia otra habitación mucho más grande que la anterior. Enormes bultos de paja se extendían hasta el techo. "Ahora debes hacer lo mismo en esta habitación. Si no lo haces, verás las consecuencias de tu engaño", le dijo el monarca antes de cerrar la puerta. La suerte de la muchacha no había cambiado, y tan nerviosa se puso que se tumbó en el suelo a llorar desconsoladamente. A las doce en punto de la noche, apareció nuevamente el enano narizón que la había ayudado. "Si me das esa sortija que brilla en tus dedos, te ayudaré a convertir toda esta paja en oro", le dijo la criatura a la muchacha, y esta no dudo un segundo en cumplir su parte del trato. Para sorpresa del rey, cuando regresó a la mañana siguiente, la habitación se encontraba repleta de hilos de oro, y fue tanta su avaricia, que decidió casarse entonces con la pobre muchacha, pero a cambio debía repetir el acto mágico una vez más. Tan triste se puso aquella joven, que no tuvo más remedio que echarse a llorar durante toda la noche. Como era costumbre, el enano narizón apareció entonces a las doce de la noche y acercándose lentamente a la muchacha le dijo: "No llores más, hermosa. Te ayudaré con el rey, pero deberás entregarme algo a cambio". "No tengo más joyas que darte", exclamó la muchacha con pesadumbre, pero el enano le pidió entonces una cosa mucho más importante: "Cuando nazca tu primer hijo, deberás entregármelo sin dudar. ¿Aceptas?". La princesa no tuvo que pensarlo mucho, y tal como había prometido el enano, convirtió toda la paja de la habitación en oro usando la rueca. En las primeras horas de la mañana siguiente, el rey apareció como de costumbre, y al ver que era más rico aún gracias a la muchacha, ordenó a sus súbditos que preparan un banquete de bodas gigante para casarse de inmediato. Al cabo de un año, el rey y la nueva reina tuvieron su primer hijo, y aunque la muchacha había olvidado por completo la promesa del enano narizón, este apareció una buena noche en la ventana de su alcoba. "He venido a llevarme lo prometido. Entrégame a tu hijo como acordamos", susurró el enano entre risas. "Por favor, criatura. No te lleves lo que más amo en este mundo", suplicó la reina arrodillada, "te daré todo lo que desees, montañas de oro, mares de plata, todo porque dejes a mi hijo en paz". Pero el enano no se dejó convencer, y tanta fue la insistencia de la muchacha que finalmente, la criatura le dijo: "Sólo hay un modo de que puedas romper la promesa, y es el siguiente: dentro de tres noches vendré nuevamente a buscarte, si para ese entonces adivinas mi nombre, te dejaré en paz". Y dicho aquello se desapareció al instante. La reina, decidió entonces averiguar por todos los medios el nombre de aquella criatura, por lo que mandó a sus guardias a todos los rincones del mundo y les ordenó que no volvieran si no traían una respuesta. Tras dos días y dos noches, apareció uno de los guardias, contando la historia de un enano que había visto caminando por el bosque, mientras cantaba lo siguiente: "Soy un duende maldito, Inteligente como yo, nunca encontrarán Mañana me llevaré al niño Y el nombre de Rumpelstiltskin, jamás adivinarán" Así pudo saber la reina el nombre del enano narizón, y cuando se apareció en la noche le dijo: "Tu nombre es Rumpelstiltskin". Entre gritos y lamentos, el enano comenzó a dar saltos enfurecidos por toda la habitación, y tanto fue su enfado, que saltando y saltando llegó al borde del balcón y se cayó en el foso del castillo, quedando atrapado allí para siempre.')
    # exa1=['Enano Saltarin'.lower(),example_text1]  
    # #Caperucita   
    # example_text2 = (u'Érase una vez una niña que era muy querida por su abuelita, a la que visitaba con frecuencia aunque vivía al otro lado del bosque. Su madre que sabía coser muy bien le había hecha una bonita caperuza roja que la niña nunca se quitaba, por lo que todos la llamaban Caperucita roja.Una tarde la madre la mandó a casa de la abuelita que se encontraba muy enferma, para que le llevara unos pasteles recién horneados, una cesta de pan y mantequilla. – "Caperucita anda a ver cómo sigue tu abuelita y llévale esta cesta que le he preparado", –le dijo. Además le advirtió: –"No te apartes del camino ni hables con extraños, que puede ser peligroso". Caperucita que siempre era obediente asintió y le contestó a su mamá: – "No te preocupes que tendré cuidado". Tomó la cesta, se despidió cariñosamente y emprendió el camino hacia casa de su abuelita, cantando y bailando como acostumbraba. No había llegado demasiado lejos cuando se encontró con un lobo que le preguntó: – "Caperucita, caperucita ¿a dónde vas con tantas prisas?"Cuento de Caperucita Roja Caperucita lo miró y pensó en lo que le había pedido su mamá antes de salir, pero como no sintió temor alguno le contestó sin recelo. – "A casa de mi abuelita, que está muy enfermita". A lo que el lobo replicó: – "¿Y d ó nde vive tu abuelita?". – "Más allá de donde termina el bosque, en un claro rodeado de grandes robles". – Respondió Caperucita sin sospechar que ya el lobo se deleitaba pensando en lo bien que sabría. El lobo que ya había decidido comerse a Caperucita, pensó que era mejor si primero tomaba a la abuelita como aperitivo. – "No debe estar tan jugosa y tierna, pero igual servirá", – se dijo mientras ideaba un plan. Mientras acompañaba a esta por el camino, astutamente le sugirió: – "¿Sabes qué haría realmente feliz a tu abuelita? Si les llevas algunas de las flores que crecen en el bosque". Caperucita también pensó que era una buena idea, pero recordó nuevamente las palabras de su mamá. – "Es que mi mamá me dijo que no me apartara del camino". A lo que el lobo le contestó: – "¿Ves ese camino que está a lo lejos? Es un atajo con el que llegarás más rápido a casa de tu abuelita". Sin imaginar que el lobo la había engañado, esta aceptó y se despidió de él. El lobo sin perder tiempo alguno se dirigió a la casa de la abuela, a la que engañó haciéndole creer que era su nieta Caperucita. Luego de devorar a la abuela se puso su gorro, su camisón y se metió en la cama a esperar a que llegase el plato principal de su comida. A los pocos minutos llegó Caperucita roja, quien alegremente llamó a la puerta y al ver que nadie respondía entró. La niña se acercó lentamente a la cama, donde se encontraba tumbada su abuelita con un aspecto irreconocible. Cuento infantil de Caperucita Roja– "Abuelita, que ojos más grandes tienes", – dijo con extrañeza. – "Son para verte mejor", – dijo el lobo imitando con mucho esfuerzo la voz de la abuelita. – "Abuelita, pero que orejas tan grandes tienes" – dijo Caperucita aún sin entender por qué su abuela lucía tan cambiada. – "Son para oírte mejor", – volvió a decir el lobo. – "Y que boca tan grande tienes". – "Para comerte mejooooooooor", – chilló el lobo que diciendo esto se abalanzó sobre Caperucita, a quien se comió de un solo bocado, igual que había hecho antes con la abuelita. En el momento en que esto sucedía pasaba un cazador cerca de allí, que oyó lo que parecía ser el grito de una niña pequeña. Le tomó algunos minutos llegar hasta la cabaña, en la que para su sorpresa encontró al lobo durmiendo una siesta, con la panza enorme de lo harto que estaba. El cazador dudó si disparar al malvado lobo con su escopeta, pero luego pensó que era mejor usar su cuchillo de caza y abrir su panza, para ver a quién se había comido el bribón. así fue como con tan solo dos cortes logró sacar a Caperucita y a su abuelita, quienes aún estaban vivas en el interior del lobo. Entre todos decidieron darle un escarmiento al lobo, por lo que le llenaron la barriga de piedras y luego la volvieron a coser. Al despertarse este sintió una terrible sed y lo que pensó que había sido una mala digestión. Con mucho trabajo llegó al arroyo más cercano y cuando se acercó a la orilla, se tambaleó y cayó al agua, donde se ahogó por el peso de las piedras. Caperucita roja aprendió la lección y pidió perdón a su madre por desobedecerla. En lo adelante nunca más volvería a conversar con extraños o a entretenerse en el bosque.')
    # exa2=['Caperucita  Roja'.lower(),example_text2]
    # #Gato con Botas
    # example_text3=(u'Érase una vez un viejo molinero que tenía tres hijos. El molinero solo tenía tres posesiones para dejarles cuando muriera: su molino, un asno y un gato. Estaba en su lecho de muerte cuando llamó a sus hijos para hacer el reparto de su herencia. –"Hijos míos, quiero dejarles lo poco que tengo antes de morir", les dijo. Al hijo mayor le tocó el molino, que era el sustento de la familia. Al mediano le dejó al burro que se encargaba de acarrear el grano y transportar la harina, mientras que al más pequeño le dejó el gato que no hacía más que cazar ratones. Dicho esto, el padre murió. El hijo más joven estaba triste e inconforme con la herencia que había recibido. –"Yo soy el que peor ha salido ¿Para qué me puede servir este gato?", – pensaba en voz alta. El gato que lo había escuchado, decidió hacer todo lo que estuviese a su alcance para ayudar a su nuevo amo. – "No te preocupes joven amo, si me das un bolso y un par de botas podremos salir a recorrer el mundo y verás cuántas riquezas conseguiremos juntos". El joven no tenía muchas esperanzas con las promesas del gato, pero tampoco tenía nada que perder. Si se quedaba en aquella casa moriría de hambre o tendría que depender de sus hermanos, así que le dio lo que pedía y se fueron a recorrer el mundo. Caminaron y caminaron durante días hasta que llegaron a un reino lejano. El gato con botas había escuchado que al rey de aquel país le gustaba comer perdices, pero como eran tan escurridizas se hacían casi imposibles de conseguir. Mientras que el joven amo descansaba bajo la sombra de un árbol, el gato abrió su bolsa, esparció algunos granos que le quedaban sobre ella y se escondió a esperar.Llevaba un rato acechando cuando aparecieron un grupo de perdices, que encontraron el grano y se fueron metiendo una a una en el saco para comérselo. Cuando ya había suficientes, el gato tiró de la cuerda que se encontraba oculta, cerrando el saco y dejando atrapadas a las perdices. Luego se echó el saco al hombro y se dirigió al palacio para entregárselas al rey.Cuando se presentó ante el rey le dijo: – "Mi rey, el Marqués de Carabás le envía este obsequio. (Este fue el nombre que se le ocurrió darle a su amo)". El rey complacido aceptó aquella oferta y le pidió que le agradeciera a su señor. Pasaron los días y el gato seguía mandándole regalos al rey, siempre de parte de su amo.Un día el gato se enteró de que el rey iba a pasear con su hermosa hija cerca de la ribera del río y tuvo una idea. Le dijo a su amo: – "Si me sigues la corriente podrás hacer una fortuna, solo quítate la ropa y métete al río". Así lo hizo el hijo del molinero hasta que escuchó a su gato gritando: – "¡Socorro! ¡Auxilio! ¡Se ahoga el Marqués de Carabás! ¡Le han robado sus ropas!".El rey atraído por los gritos se acercó a ver qué pasaba. Al ver que se trataba del Marqués que tantos obsequios le había enviado, lo envolvió en ropas delicadas y lo subió en su carruaje para que les acompañara en el paseo.El astuto gato se adelantó a la comitiva real y se dirigió a las tierras de un temido ogro, donde se encontraban trabajando unos campesinos. Los amenazó diciéndoles: – "Cuando el rey pase por aquí y les pregunte de quién son estas tierras, deberán responder que pertenecen al Marqués de Carabás, sino morirán".De esta manera cuando el rey cruzó con su carruaje y preguntó a quién pertenecían aquellas tierras, todos los campesinos contestaron: – "Son del señor Marqués de Carabás".El gato con botas que se sentía muy complacido con su plan, se dirigió luego al castillo del ogro, pensando en reclamarlo para su amo. Ya había escuchado todo lo que el ogro podía hacer y lo mucho que le gustaba que lo adularan. Así que se anunció ante él con el pretexto de haber viajado hasta allí para presentarle sus respetos.Cuando estuvo solo con el ogro, el gato le dijo: – "Me han dicho que es capaz de convertirse en cualquier clase de animal, como por ejemplo un elefante o un león".– "Es cierto", – contestó el ogro muy halagado y se transformó de inmediato en un rugiente león para demostrarlo. A lo que el gato contestó: – "¡Sorprendente! ¡Ha sido increíble! Pero me impresionaría más si pudieras transformarte en algo tan pequeñito como un ratón. Eso debe ser imposible, incluso para un ogro tan poderoso como tú". El ogro ansioso por impresionar al gato, se convirtió en un segundo en un diminuto ratón, pero apenas lo hizo el gato se lanzó sobre él y se lo tragó de un bocado. Fue así como el gato reclamó aquel palacio y las tierras circundantes para el recién nombrado Marques de Carabás, su joven amo. Allí recibió al rey, que impresionado ante el lujo y la majestuosidad del castillo, le propuso de inmediato la mano de su hija en matrimonio. El hijo del molinero aceptó y luego de que el rey murió gobernó aquellas tierras, al lado de el gato con botas a quien nombró primer ministro.')
    # exa3=['Gato con Botas'.lower(),example_text3]
  
    # r1 = qagenerator.make_simple_questions(exa1[0], exa1[1])
    # print('***LISTA DE PREGUNTAS:\n',*r1, sep = "\n")
    # r2 = qagenerator.make_simple_questions(exa2[0], exa2[1])
    # r3 = qagenerator.make_simple_questions(exa3[0], exa3[1])
