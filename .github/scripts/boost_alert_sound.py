from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""  function beep(){const ctx=getAudio();if(!ctx)return;try{const now=ctx.currentTime;[0,.18].forEach((offset,index)=>{const osc=ctx.createOscillator(),gain=ctx.createGain();osc.type='sine';osc.frequency.value=index?720:920;gain.gain.setValueAtTime(.0001,now+offset);gain.gain.exponentialRampToValueAtTime(.18,now+offset+.02);gain.gain.exponentialRampToValueAtTime(.0001,now+offset+.16);osc.connect(gain);gain.connect(ctx.destination);osc.start(now+offset);osc.stop(now+offset+.18)})}catch(error){}}"""
new="""  function beep(){const ctx=getAudio();if(!ctx)return;try{const now=ctx.currentTime;const master=ctx.createGain();master.gain.setValueAtTime(.72,now);master.connect(ctx.destination);const bursts=[{t:0,f:880,d:.18},{t:.22,f:660,d:.18},{t:.44,f:1040,d:.22},{t:.72,f:660,d:.18},{t:.94,f:1120,d:.24}];bursts.forEach(({t,f,d},index)=>{const osc=ctx.createOscillator(),gain=ctx.createGain();osc.type=index%2?'sawtooth':'square';osc.frequency.setValueAtTime(f,now+t);if(index===2)osc.frequency.linearRampToValueAtTime(1320,now+t+d);gain.gain.setValueAtTime(.0001,now+t);gain.gain.exponentialRampToValueAtTime(.48,now+t+.018);gain.gain.setValueAtTime(.48,now+t+Math.max(.03,d-.045));gain.gain.exponentialRampToValueAtTime(.0001,now+t+d);osc.connect(gain);gain.connect(master);osc.start(now+t);osc.stop(now+t+d+.02)});setTimeout(()=>{try{master.disconnect()}catch(error){}},1400)}catch(error){}}"""
if old not in s:
    raise SystemExit('old beep function not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('strong alert sound patched')
