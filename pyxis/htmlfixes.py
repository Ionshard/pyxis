subs = (
    #Sirius USA
    ('width="100"%"', 'width="100%"'),

    #Sirius Canada
    (r'style=["\']?(\{.*\})["\']?', r'style="\1" '),
    (r'width=["\']?(\d+)["\']?', r'width="\1"'),
    (r'width="100"%"', r'width="100%"'),
    #(r'onclick=["\']?([^\s<>]*)["\']?', r'onclick=""'),
    (r'onclick=location.href', r'href'),

)

__all__ = ['subs']
