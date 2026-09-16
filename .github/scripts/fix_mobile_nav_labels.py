from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='''  <style id="mobile-nav-labels-fix">
    @media(max-width:700px){
      .nav{grid-template-columns:repeat(6,minmax(0,1fr))!important}
      .nav-item{display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:3px;padding:5px 1px!important;min-width:0}
      .nav-item svg{width:17px;height:17px;flex:none}
      .nav-item span{display:block!important;font-size:7px!important;line-height:1;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:100%}
      .nav-count{position:absolute;top:2px;right:4px;transform:scale(.82)}
      .nav-item{position:relative}
    }
  </style>
'''
if 'id="mobile-nav-labels-fix"' not in s:
    if '</head>' not in s: raise SystemExit('head marker not found')
    s=s.replace('</head>',marker+'</head>',1)
p.write_text(s,encoding='utf-8')
print('mobile nav labels fixed')
