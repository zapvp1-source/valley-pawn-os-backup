STORES={
 "culpeper":dict(name="Culpeper",addr="571 James Madison Highway",zip="22701",street="571 James Madison Highway",phone="(540) 445-5510",tel="+15404455510",email="culpeper@fcfpawn.com",rating="4.9",count=425,six=True,pid=419,
   areas="Culpeper County, Orange, Madison, Remington, Brandy Station, Rixeyville, Warrenton and Sperryville",
   lat=None),
 "waynesboro":dict(name="Waynesboro",addr="1321 West Broad Street",zip="22980",street="1321 West Broad Street",phone="(540) 221-6346",tel="+15402216346",email="waynesboro@fcfpawn.com",rating="4.9",count=375,six=False,pid=420,
   areas="Staunton, Stuarts Draft, Fishersville, Crozet, Grottoes, Lyndhurst and the rest of Augusta County"),
 "harrisonburg":dict(name="Harrisonburg",addr="1790 East Market Street",zip="22801",street="1790 East Market Street",phone="(540) 574-4500",tel="+15405744500",email="harrisonburg@fcfpawn.com",rating="4.9",count=336,six=False,pid=421,
   areas="Rockingham County, Bridgewater, Dayton, Broadway, Timberville, Elkton, McGaheysville, Mount Crawford and Penn Laird"),
 "lexington":dict(name="Lexington",addr="125 Walker Street",zip="24450",street="125 Walker Street",phone="(540) 461-8349",tel="+15404618349",email="lexington@fcfpawn.com",rating="4.8",count=197,six=False,pid=422,
   areas="Rockbridge County, Buena Vista, Glasgow, Natural Bridge, Fairfield, Raphine and Goshen"),
 "roanoke":dict(name="Roanoke",addr="2362 Peters Creek Road, Suite C",zip="24017",street="2362 Peters Creek Road, Suite C",phone="(540) 562-0776",tel="+15405620776",email="roanoke@fcfpawn.com",rating="4.9",count=292,six=True,pid=423,
   areas="Salem, Vinton, Hollins, Cave Spring, Northwest Roanoke and the rest of the Roanoke Valley"),
}
ASOF="October 2026"
def hours_text(s):
    return "Monday–Friday 10 AM–6 PM and Saturday 10 AM–5 PM (closed Sunday)" if s["six"] else "Monday, Tuesday, Thursday, Friday and Saturday 10 AM–6 PM (closed Wednesday and Sunday)"
def hours_spec(s):
    if s["six"]:
        return [{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"10:00","closes":"18:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":["Saturday"],"opens":"10:00","closes":"17:00"}]
    return [{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Thursday","Friday","Saturday"],"opens":"10:00","closes":"18:00"}]
def maps(s): return "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+"+s["name"]+"+VA"
