import os

html = open('index.html', 'r', encoding='utf-8').read()

# 1. Remove the gold box-shadow from .playable
html = html.replace('.playing-card.playable { box-shadow: 0 0 0 4px var(--gold), 0 10px 20px rgba(0,0,0,0.2); }',
                    '.playing-card.playable { box-shadow: 0 5px 15px rgba(0,0,0,0.1); }')

# 2. Remove the CSS gradient backgrounds (twotoneStyle) from renderBoard and renderBoardClient
import re

# We will just replace the innerHTML generation to not use twotoneStyle at all.
# For discard pile (renderBoard):
html = html.replace('''    if (topCard.action === 'wild' && topCard.activeColors) {
      twotoneStyleTop = `background: ${cMap[topCard.activeColors[0]]}; padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    } else if (topCard.color.length === 2) {
      const c1 = cMap[topCard.color[0]];
      const c2 = cMap[topCard.color[1]];
      twotoneStyleTop = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    }
    pileDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyleTop}"><img src="${topCard.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;''', 
    '''    pileDiv.innerHTML = `<div style="width:100%; height:100%;"><img src="${topCard.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);"></div>`;''')

# For player hand (renderBoard):
html = html.replace('''    let twotoneStyle = '';
    const cMap = { green: '#22c55e', red: '#ef4444', blue: '#3b82f6', yellow: '#eab308' };
    if (card.color.length === 2) {
      const c1 = cMap[card.color[0]];
      const c2 = cMap[card.color[1]];
      twotoneStyle = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    }
    
    cardDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyle}"><img src="${card.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;''',
    '''    cardDiv.innerHTML = `<div style="width:100%; height:100%;"><img src="${card.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);"></div>`;''')

# For discard pile (renderBoardClient):
html = html.replace('''    if (topCard.action === 'wild' && topCard.activeColors) {
      twotoneStyleTop = `background: ${cMap[topCard.activeColors[0]]}; padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    } else if (topCard.color.length === 2) {
      const c1 = cMap[topCard.color[0]];
      const c2 = cMap[topCard.color[1]];
      twotoneStyleTop = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    }
    pileDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyleTop}"><img src="${topCard.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;''',
    '''    pileDiv.innerHTML = `<div style="width:100%; height:100%;"><img src="${topCard.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);"></div>`;''')

# For player hand (renderBoardClient):
html = html.replace('''      let twotoneStyle = '';
      const cMap = { green: '#22c55e', red: '#ef4444', blue: '#3b82f6', yellow: '#eab308' };
      if (card.color.length === 2 && !card.action) {
        const c1 = cMap[card.color[0]];
        const c2 = cMap[card.color[1]];
        twotoneStyle = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
      }
      
      cardDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyle}"><img src="${card.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;''',
      '''      cardDiv.innerHTML = `<div style="width:100%; height:100%;"><img src="${card.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);"></div>`;''')

# One thing to fix: the complex cards in Zukan (Card list) also don't need borders. But zukan just renders `c.img`.
open('index.html', 'w', encoding='utf-8').write(html)
