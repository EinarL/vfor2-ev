# Sölusíðan
Ég ákvað að búa til síðu þar sem fólk getur selt hluti sína og keypt það sem aðrir eru að selja. (Það er ekki nein korta virkni til að kaupa á síðunni, þessi síða er ekki hugsuð til að vera eins og ebay eða amazon, heldur frekar eins og síða eins og bland.is þar sem notendurnir myndu þurfa að sjá um greiðsluna sjálfir)

Fyrir þetta verkefni notaði ég Django, ég ákvað að nota það einungis vegna þess að Python er uppáhalds forritunartungumálið mitt. Ég vissi ekkert hvernig það er áður en ég byrjaði að nota það en það er miklu betra en ég hélt að það væri.

Annað sem ég ætti að minnast á er að ég nota AJAX til að senda requests á bakendann án þess að þurfa að refresha síðunni, ég nota það á nokkrum stöðum eins og að replya, likea comment og sækja fleiri comments.

Þau skylirði sem ég uppfylli eru eftirfarandi:
+ Notendaumsjón
  - Það sem er nice við Django er að það gerir þetta meira auðvelt fyrir mann að útfæra vegna þess að það býr sjálfkrafa til SQL töflu fyrir notendur, hashar passwordin, og að það validatar username og password sjálfkrafa.
  - Ég passa upp á að notendurnir sem eru ekki innskráðir geta ekki farið inn á síður þar sem maður þarf að vera innskráður (eins og create listing síðuna), til þess þarf bara að hafa `@login_required` fyrir ofan viewið í views.py og þá mun notandinn vera færður yfir á login síðuna ef hann reynir að fara á þessa síðu án þess að vera innskráður.
  - Einnig passa ég upp á að notendur sem eru ekki innskráðir geta ekki like-að comment eða commentað.
+ Bakendi
  - Ég nota Django sem bakenda.
+ Gagnagrunnur
  - Ég nota PostgreSQL
  - Þar geymi ég efirfarandi töflur (ásamt þeim sem Django bjó til sjálfkrafa eins og users töfluna):
    * `listing`, heldur utan um upplýsingar varðandi það sem fólk er að selja, það hefur m.a. dálkana, title, description, price og user_id.
    * `image`, heldur utan um allar myndir sem eru til. það hefur dálk, imageURL, sem er cloudinary url fyrir myndina, og svo listing_id sem er foreign key sem tengir myndina við listing.
    * `comment`, heldur utan um öll comments
    * `reply` heldur utan um öll replies. Replies eru aðeins öðruvísi en comments vegna þess að það er ekki hægt að likea þau.
    * `upvote` heldur utan um öll upvotes. þetta þarf til þess að passa upp á það að sami notandi getur ekki likeað sama comment oftar en einu sinni.
+ Framendi
  - Það sem fylgir Django er template mál sem er mjög líkt ejs þar sem það er hægt að nota Python kóða inn í html skrá.

### Hvernig gekk?

Það er margt sem gekk mjög vel sérstaklega vegna þess að hversu auðvelt Django lætur hlutina vera. Eins og ég var búinn að minnast á að ofan, þá hjálpar Django mikið við með notendaumsjónina. En ekki bara það, ég þurfti til dæmis ekki að skrifa neinn SQL kóða, Django býr til töflurnar út frá hvernig ég skilgreini þær í models.py skránni, og svo fylgir Admin síða þar sem notandi sem er "administrator" getur bætt við, breytt og eytt gögnum, þannig maður þarf ekki einu sinni að snerta databaseinn nema ef maður sérstaklega vill það.

Annað sem var auðvelt og gekk vel er að nota `Paginator` í Django, þar sem á síðunni minni er hægt að fletta í gegnum "listings", það myndi vanalega þurfa að skrifa mikinn kóða til að útfæra þessa virkni en það var mjög auðvellt að útfæra þetta með því að nota `Paginator`.

Það er í raun og veru lítið sem ekkert sem gekk illa, það sem ég var mest að vesenast með og tók smá tíma myndi ég segja að væri kóðinn á bakvið mynda virknina á Create listing síðunni. Semsagt JavaScript og HTML kóðinn sem höndlar því að fá images og svo senda þær á bakendann.
