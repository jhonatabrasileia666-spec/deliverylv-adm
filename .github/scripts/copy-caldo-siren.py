from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old=re.search(r"  function beep\(\)\{.*?\}\n  function vibrate\(\)\{.*?\}",s,re.S)
if not old:
    raise SystemExit('alert sound functions not found')

new="""  function beep(){
    const ctx=getAudio();if(!ctx)return;
    const tone=(freq,duration,delay=0)=>{
      window.setTimeout(()=>{
        try{
          const now=ctx.currentTime;
          const osc=ctx.createOscillator();
          const gain=ctx.createGain();
          osc.type='square';
          osc.frequency.value=freq;
          gain.gain.setValueAtTime(.0001,now);
          gain.gain.exponentialRampToValueAtTime(.25,now+.02);
          gain.gain.exponentialRampToValueAtTime(.0001,now+duration);
          osc.connect(gain);gain.connect(ctx.destination);
          osc.start();osc.stop(now+duration);
        }catch(error){}
      },delay);
    };
    tone(880,.25,0);
    tone(1200,.25,300);
    tone(880,.35,620);
  }
  function vibrate(){try{navigator.vibrate?.([300,120,300,120,500])}catch(error){}}"""
s=s[:old.start()]+new+s[old.end():]

# Use the Caldo cadence: repeat every 3 seconds.
s=s.replace("{repeats=8,interval=6000}","{repeats:1200,interval:3000}")
s=s.replace("{repeats=10,interval=6000}","{repeats:1200,interval:3000}")
s=s.replace("{repeats:120,interval:5000}","{repeats:1200,interval:3000}")

# Keep the generic alert default at the same cadence.
s=s.replace("function start(key,title,body,{repeats=8,interval=6000}={})","function start(key,title,body,{repeats=1200,interval=3000}={})")

p.write_text(s,encoding='utf-8')
print('Caldo-style siren applied')
