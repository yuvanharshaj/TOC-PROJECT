import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
ax.set_xlim(-1.5, 11.5)
ax.set_ylim(-2.2, 3.2)
ax.axis('off')

# State coordinates
states = {
    'q0': (0.2, 1.0),
    'q1': (2.2, 1.0),
    'q2': (4.2, 1.0),
    'q3': (6.2, 1.0),
    'q4': (8.2, 1.0),
    'q5': (10.2, 1.0),
    'q_word': (5.2, -1.0)
}

# State sublabels
sublabels = {
    'q0': 'Start / Boundary',
    'q1': "Saw 'E'",
    'q2': "Saw 'ER'",
    'q3': "Saw 'ERR'",
    'q4': "Saw 'ERRO'",
    'q5': "Saw 'ERROR'",
    'q_word': 'Trap State'
}

# Draw states
for name, (x, y) in states.items():
    if name == 'q5':
        c1 = plt.Circle((x, y), 0.54, edgecolor='#1E40AF', fill=False, lw=2.5)
        c2 = plt.Circle((x, y), 0.45, edgecolor='#1E40AF', fill=True, facecolor='#DBEAFE', lw=1.5)
        ax.add_patch(c1)
        ax.add_patch(c2)
    elif name == 'q0':
        c = plt.Circle((x, y), 0.5, edgecolor='#047857', fill=True, facecolor='#D1FAE5', lw=2)
        ax.add_patch(c)
        # Start indicator arrow
        ax.annotate('', xy=(x - 0.5, y), xytext=(x - 1.2, y),
                    arrowprops=dict(arrowstyle='->', lw=2, color='#047857'))
        ax.text(x - 1.15, y + 0.15, 'START', fontsize=9, fontweight='bold', color='#047857', fontfamily='serif')
    elif name == 'q_word':
        c = plt.Circle((x, y), 0.52, edgecolor='#B91C1C', fill=True, facecolor='#FEE2E2', lw=2)
        ax.add_patch(c)
    else:
        c = plt.Circle((x, y), 0.5, edgecolor='#1E293B', fill=True, facecolor='#F8FAFC', lw=2)
        ax.add_patch(c)
    
    color = '#B91C1C' if name == 'q_word' else ('#047857' if name == 'q0' else ('#1E40AF' if name == 'q5' else '#0F172A'))
    ax.text(x, y + 0.05, name, ha='center', va='center', fontsize=12, fontweight='bold', color=color, fontfamily='serif')
    ax.text(x, y - 0.22, sublabels[name], ha='center', va='center', fontsize=7.5, color='#475569', fontfamily='serif')

# Forward transitions
fwd = [
    ('q0', 'q1', "'E'"),
    ('q1', 'q2', "'R'"),
    ('q2', 'q3', "'R'"),
    ('q3', 'q4', "'O'"),
    ('q4', 'q5', "'R'"),
]

for src, dst, sym in fwd:
    x1, y1 = states[src]
    x2, y2 = states[dst]
    ax.annotate('', xy=(x2 - 0.5, y2), xytext=(x1 + 0.5, y1),
                arrowprops=dict(arrowstyle='->', lw=2, color='#1E40AF', shrinkA=0, shrinkB=0))
    ax.text((x1 + x2)/2, y1 + 0.2, sym, ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1E40AF', fontfamily='serif')

# Self-loop on q0 (Non-word)
ax.annotate('', xy=(states['q0'][0] - 0.25, 1.48), xytext=(states['q0'][0] + 0.25, 1.48),
            arrowprops=dict(arrowstyle='<-', lw=1.5, color='#047857', connectionstyle='arc3,rad=-1.2'))
ax.text(states['q0'][0], 2.1, 'Non-Word', ha='center', va='bottom', fontsize=8.5, color='#047857', fontfamily='serif')

# Self-loop on q_word (Word characters)
ax.annotate('', xy=(states['q_word'][0] - 0.25, -1.5), xytext=(states['q_word'][0] + 0.25, -1.5),
            arrowprops=dict(arrowstyle='<-', lw=1.5, color='#B91C1C', connectionstyle='arc3,rad=-1.2'))
ax.text(states['q_word'][0], -2.0, 'Any Word Character', ha='center', va='top', fontsize=8.5, color='#B91C1C', fontfamily='serif')

# Acceptance: q5 to q0 match emission (curved over top)
ax.annotate('', xy=(states['q0'][0] + 0.1, 1.5), xytext=(states['q5'][0] - 0.1, 1.54),
            arrowprops=dict(arrowstyle='->', lw=2, color='#047857', connectionstyle='arc3,rad=0.32', linestyle='--'))
ax.text(5.2, 2.7, 'Non-Word Character or EOF  [EMIT MATCH & RESET TO q0]',
        ha='center', va='center', fontsize=9.5, fontweight='bold', color='#047857', fontfamily='serif',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECFDF5', edgecolor='#059669', lw=1.2))

# q_word to q0 (reset on non-word)
ax.annotate('', xy=(states['q0'][0] + 0.2, 0.55), xytext=(states['q_word'][0] - 0.45, -0.75),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#475569', connectionstyle='arc3,rad=0.15'))
ax.text(2.3, -0.25, 'Non-Word (reset to q0)', ha='center', va='center', fontsize=8.5, color='#475569', fontfamily='serif')

# q5 to q_word on word character (boundary violation)
ax.annotate('', xy=(states['q_word'][0] + 0.4, -0.7), xytext=(states['q5'][0] - 0.3, 0.5),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#B91C1C', connectionstyle='arc3,rad=0.15'))
ax.text(8.2, -0.2, 'Word Char (boundary fail)', ha='center', va='center', fontsize=8.5, color='#B91C1C', fontfamily='serif')

# Non-matching prefix transitions to q_word
for st in ['q1', 'q2', 'q3', 'q4']:
    xs, ys = states[st]
    ax.annotate('', xy=(states['q_word'][0], -0.45), xytext=(xs, ys - 0.5),
                arrowprops=dict(arrowstyle='->', lw=1.0, color='#94A3B8', connectionstyle='arc3,rad=-0.08'))

ax.text(5.2, 0.15, 'Mismatched Word Characters -> Trap State', ha='center', va='center', fontsize=8, color='#64748B', style='italic', fontfamily='serif')

# Title annotation
ax.text(5.2, 3.15, 'State Transition Diagram for DFAErrorScanner  M = (Q, Sigma, delta, q0, F)',
        ha='center', va='top', fontsize=12, fontweight='bold', color='#0F172A', fontfamily='serif')

plt.tight_layout()
plt.savefig('docs/dfa_state_diagram.png', dpi=300, bbox_inches='tight')
print('Successfully generated docs/dfa_state_diagram.png')
