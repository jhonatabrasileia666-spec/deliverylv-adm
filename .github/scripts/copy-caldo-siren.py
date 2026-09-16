from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_beep="function beep(){const ctx=getAudio();if(!ctx)return;try{const now=ctx.currentTime;const master=ctx.createGain();master.gain.setValueAtTime(.72,now);master.connect(ctx.destination);const bursts=[{t:0,f:880,d:.18},{t:.22,f:660,d:.18},{t:.44,f:1040,d:.22},{t:.72,f:660,d:.18},{t:.94,f:1120,d:.24}];bursts.forEach(({t,f,d},index)=>{const osc=ctx.createOscillator(),gain=ctx.createGain();osc.type=index%2?'sawtooth':'square';osc.frequency.setValueAtTime(f,now+t);if(index===2)osc.frequency.linearRampToValueAtTime(1320,now+t+d);gain.gain.setValueAtTime(.0001,now+t);gain.gain.exponentialRampToValueAtTime(.48,now+t+.018);gain.gain.setValueAtTime(.48,now+t+Math.max(.03,d-.045));gain.gain.exponentialRampToValueAtTime(.0001,now+t+d);osc.connect(gain);gain.connect(master);osc.start(now+t);osc.stop(now+t+d+.02)});setTimeout(()=>{try{master.disconnect()}catch(error){}},1400)}catch(error){}}"
old_vibrate="function vibrate(){try{navigator.vibrate?.([260,120,260,120,420])}catch(error){}}"
if old_beep not in s or old_vibrate not in s:
    raise SystemExit('current alert sound functions not found')

new_beep="""function beep(){
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
  }"""
new_vibrate="function vibrate(){try{navigator.vibrate?.([300,120,300,120,500])}catch(error){}}"
s=s.replace(old_beep,new_beep,1).replace(old_vibrate,new_vibrate,1)

# Same cadence as the Caldo panel: every 3 seconds.
s=s.replace("{repeats:8,interval:6000}","{repeats:1200,interval:3000}")
s=s.replace("{repeats:10,interval:6000}","{repeats:1200,interval:3000}")
s=s.replace("{repeats:120,interval:5000}","{repeats:1200,interval:3000}")
s=s.replace("function start(key,title,body,{repeats=8,interval=6000}={})","function start(key,title,body,{repeats=1200,interval=3000}={})")

p.write_text(s,encoding='utf-8')
print('Caldo-style siren applied safely')
