import re


EPOCH_TIME_CAPTURE = r"Total time for fitting: \d+.\d+s"
EPOCH_CAPTURE = r"Epoch: [0-9]+\/[0-9]+, (?:\w+: +-?[0-9]+\.[0-9s ]+)+"

def parse_rounds(rounds, func):
    out = []
    for r in rounds:
        round_number = int(r.split('\n')[0])
        try:
            out.append(func(r))
            if round_number == 0:
                break
        except Exception as e:
            print('Failed to parse: '+ str(e))
    return out[::-1]

def parse_time(r):
    time = re.findall(EPOCH_TIME_CAPTURE, r)[0]
    time = time.split()[-1][:-1]
    return time


def parse_metrics(r):
    
    def get_metric_from_text(txt):
        if 'Epoch' in txt:
            txt_split = txt.split(' ')
            txt = txt_split[-2]+' '+txt_split[-1]
        if txt[-1]=='s':
            txt = txt[:-1]

        return txt.split(': ')

    metrics = re.findall(EPOCH_CAPTURE, r)[0]
    metrics_dct = dict([get_metric_from_text(e) for e in metrics.split('  ') if e.strip()!=''])

    return metrics_dct


def parse_log(log):
    
    rounds = log.split('Get global model for round:')[:0:-1]
    
    times = parse_rounds(rounds, parse_time)
    metrics = parse_rounds(rounds, parse_metrics)
    
    return {'round_time': times, 'metrics': metrics}
