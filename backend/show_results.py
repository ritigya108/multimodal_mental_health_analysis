import json, os
base = os.path.join(os.path.dirname(__file__), 'checkpoints', 'eatd')

with open(os.path.join(base, 'final_metrics.json')) as f:
    m = json.load(f)

print("=== FINAL DEV METRICS (EATD Real Data) ===")
for k, v in m.items():
    print("  {:12s}: {:.4f}".format(k, v))

with open(os.path.join(base, 'history.json')) as f:
    h = json.load(f)

print()
print("=== TRAINING HISTORY ===")
print("  {:5} {:11} {:11} {:9} {:9} {:8}".format("Epoch","TrainLoss","TrainAcc","TrainF1","DevAcc","DevF1"))
for tr, dv in zip(h['train'], h['dev']):
    print("  {:5} {:11.4f} {:11.3f} {:9.3f} {:9.3f} {:8.3f}".format(
        tr['epoch']+1, tr['loss'], tr['accuracy'], tr['f1'],
        dv['accuracy'], dv['f1']
    ))
