# eBay item-specifics fill queue (>=$100 listings, <5 specifics)

Generated 2026-08-23 from the audit data. NOT auto-filled — see reasoning below.

## Why this is a candidate list, not an auto-applied fix

Item specifics (Body Material, Storage, Ring Size, etc.) require real per-item facts —
guessing them from the title risks the exact failure the 2026-08-22 incident produced on
the Sony ZV-E10 listing (a fabricated "Body" claim contradicted by the item's own MPN).
The existing `ebay-weekly-quality-fix` and `ebay-title-photo-accuracy-audit` weekly tasks
already do this kind of enrichment carefully, cross-checking full-res photos before writing
anything. This list hands them a prioritized queue (highest-value listings first) instead of
letting a bulk script assert facts nobody verified.

| Store | Item | Price | Specifics now | Title |
|---|---|---:|---:|---|
| Waynesboro | 800508952383 | $5999.99 | 0 | Tomahawk® 1500 Plasma Cutter with 25 ft (7.6 m) Hand Torch |
| Culpeper | 397873604725 | $4499.99 | 0 | Vintage Oberheim OB-SX Synthesizer (Tested) |
| Harrisonburg | 800492639146 | $2499.99 | 0 | 1989 VMI Virginia Military Institute Sterling Silver Medal/Medallion # |
| Culpeper | 395544604340 | $1599.99 | 0 | Size: 7 .900 Polished Platinum Round Brilliant Cut Solitaire Diamond R |
| Culpeper | 397521402078 | $1519.99 | 0 | Jackson Rhoads Professional Series 6-String Electic Guitar (Custom) |
| Culpeper | 398204785291 | $1499.99 | 0 | Uncirculated United States Currency $1-$10 Lot Of 12 PCS Coin |
| Harrisonburg | 800493301543 | $1299.94 | 0 | Vintage Omega Constellation Automatic Chronometer Day-Date wristwatc |
| Roanoke | 298235812990 | $1259.99 | 0 | David Yurman 20" Sterling Silver 14k Yellow Gold Cable Oval Link Neckl |
| Waynesboro | 800471578856 | $1249.94 | 0 | Case Knife 75th Anniversary 1980 Collectors set of 7 Knives w/ Display |
| Culpeper | 397744355473 | $1239.99 | 0 | Vintage 1960's Glen Campbell Ovation 1127-4 Acoustic Guitar |
| Culpeper | 398165117706 | $1127.99 | 0 | iBUYPOWER - Scale Gaming Desktop PC - Intel Core i5 14400F - NVIDIA |
| Culpeper | 397235452413 | $1039.99 | 0 | Louis Vuitton S-Lock Vertical Wearable Black Taurillon Monogram Leat |
| Culpeper | 398250198969 | $1008.99 | 0 | Sig Sauer KILO3000BDX Range Finder Binoculars Green W/Box |
| Culpeper | 398297121941 | $999.99 | 0 | BOSE F1 MODEL 812 Flexible Array Loud Speaker (Tested) w/ Travel Bag |
| Culpeper | 398297211076 | $999.99 | 0 | Bose F1 Model 812 Flexible Array Loud Speaker (Tested) w/ Travel Bag |
| Waynesboro | 800548737480 | $999.99 | 0 | Sony Alpha a7 III Mirrorless Camera Body Black 24.2MP Wi-Fi NFC HDMI |
| Culpeper | 398249428099 | $899.99 | 0 | Eminem The Eminem Show Signed / Authenticated, Album, LP, Vinyl |
| Culpeper | 398207439536 | $799.99 | 0 | Honda EB6500X Portable Gas Powered Generator - Tested & Running |
| Waynesboro | 800548737511 | $799.99 | 0 | Diminutive Federico Jimenez Sterling Turqoise Mini Squash Necklace |
| Culpeper | 397872521972 | $764.99 | 0 | 70's-80's Epiphone Genesis Dark Sunburst Ebony 6-String Electric Guita |
| Culpeper | 398204587150 | $749.99 | 0 | Paul Reed Smith PRS SE Swamp Ash Special Iri Blue Electric Guitar w/ G |
| Lexington | 158030380480 | $729.99 | 0 | 2021 Epiphone Explorer Ebony Black Electric Guitar w/ Hard Case |
| Culpeper | 398162327204 | $720.00 | 0 | Tree of Time 1973 Franklin Mint Annual Sterling Silver Calander .925 |
| Waynesboro | 800384727660 | $649.99 | 0 | Beastie Boys Fight For Your Right Revisited Hotsauce Committee Part |
| Waynesboro | 800321499390 | $649.94 | 0 | Sony ZV-E10 Mirrorless Vlogging Camera Body with Extra Accessories - U |
| Culpeper | 398147103639 | $619.99 | 0 | Snap-On SOLUS Edge PRO EESC320 Full Function Scan Tool w/Case |
| Culpeper | 398260905935 | $599.99 | 0 | Vintage Taxco .950 Silver Inlay Choker Collar Neklace Made in Mexico 1 |
| Culpeper | 398155046400 | $599.99 | 0 | Cyberton Computer Clx Ryzen 5 5600gb w/Radeon Graphics 3.90GHZ Ram |
| Culpeper | 397940074581 | $599.99 | 0 | Snap-On Caterpillar CAT 9S-7351 Crankshaft Main Bearing Torque Wrench |
| Culpeper | 398072499300 | $599.99 | 0 | Vintage Ensoniq VFX-SD 61-Key Wavetable Music Synthesizer Workstation |
| Culpeper | 398094506911 | $599.99 | 0 | Vintage Tiffany & Co. Sterling Silver Sewing Dish/Pin Cushion Dated 19 |
| Harrisonburg | 800167632660 | $599.99 | 0 | Apple iPad Pro 12.9" 6th Gen M2 256GB Wi-Fi + Cellular Space Gray MP60 |
| Culpeper | 397743302026 | $583.99 | 0 | VITURE Pro XR/AR Glasses, 135" 120Hz Bundle |
| Culpeper | 398155091025 | $575.00 | 0 | 2020 US Mint 5 Dollar Gold Eagle 1/10 oz American Gold Coin NGC MS69 G |
| Culpeper | 398200659848 | $568.99 | 0 | AKAI MPC One Plus Standalone Drum Machine Sampler Sequencer w/ Box - T |
| Roanoke | 298390566950 | $559.00 | 0 | Mariners Anchor Charm14K 2 Tone Gold 2.1dwt |
| Culpeper | 398236013797 | $549.99 | 0 | Dewalt DWS779 Saw W/ DW7232 Table (Local Pick Up Only) |
| Culpeper | 398199722568 | $497.99 | 0 | Apple iPad Air 11-Inch M3 Chip 128GB Gray WiFi Tablet - Tested & Worki |
| Culpeper | 398263387339 | $479.99 | 0 | Hoyt Carbon Spyder FX Compound Bow w/Extras 60-70# (READ)(Derailed) Le |
| Culpeper | 397609593253 | $454.39 | 0 | TrueTone Vanguard 302 Electric Guitar (1960's) - Black (READ) |
| Lexington | 158071100077 | $439.99 | 0 | ZODIAC Gent's Wristwatch ZO2241 YELLOW AND GREEN SEA DRAGON |
| Culpeper | 398235224715 | $422.99 | 0 | Vintage Schecter Diamond C-1 Plus Maple Electric Guitar (PLEASE READ) |
| Culpeper | 397682953686 | $399.99 | 0 | New Breed Genetix Compound Bow 26 Draw 40 Draw Weight |
| Culpeper | 396879530184 | $399.99 | 0 | Bulova Accutron Accutron Oxford Watch Model 27B60 Gold- toned Stainl |
| Waynesboro | 800508953157 | $399.99 | 0 | Xreal Air 2 Pro AR Smart Glasses Bundle - Used, Tested & Working |
| Roanoke | 298565157505 | $399.99 | 0 | Lenovo Ideapad Slim 3-WIN 11 Pro, Intel Core I7 13620H 2.4GHZ, 16GB |
| Culpeper | 398235889420 | $382.99 | 0 | Dewalt D55146 4.5 Gal. Portable Electric Air Compressor 225 PSI (LOCAL |
| Roanoke | 306861872975 | $367.99 | 0 | Judith Ripka 20" Synthetic Cubic Zirconia Stone Necklace 925 Silver |
| Roanoke | 298300686494 | $359.99 | 0 | Schrade Scrimshaw 1995 Limited Edition Series-The Great American Out |
| Culpeper | 397940006530 | $349.99 | 0 | GOPRO Hero 12 Black With Battery and Portable Battery Charger Case |
| Culpeper | 398200794774 | $349.99 | 0 | Briggs & Stratton Portable Generator Model 030253 - Tested & Running |
| Roanoke | 307107327128 | $349.99 | 0 | Snap-on MT2500 Multi-Make Automotive Diagnostic Scanner Brick w/ Cable |
| Culpeper | 398113659373 | $329.99 | 0 | Festool Dual Mode Rotex RO 90 DX FEQ-Plus US Sander 3.5" (Tested) |
| Roanoke | 298505042432 | $319.99 | 0 | Ray-Ban Meta Wayfarer Gen 2 Smart Glasses with case |
| Lexington | 158096242130 | $304.99 | 0 | Auto Meter 3903 Sport-Comp Monster Shift-Lite Tachometer 10k RPM 5" NO |
| Culpeper | 398264192126 | $299.99 | 0 | Vintage Sterling Silver A701 Detailed Brandy Warmer 82.1G |
| Harrisonburg | 800283065856 | $299.99 | 0 | Canon EOS Rebel T6 1300D 18MP DSLR Camera Bundle w/ 2 Lenses & Charger |
| Lexington | 157975512781 | $299.99 | 0 | BULOVA Lady's Wristwatch 98R234 Marine Star |
| Culpeper | 397686923313 | $299.98 | 0 | Western Cutlery W49 Bowie Knife 9" Fixed Blade, Version 3 Collectible |
| Culpeper | 397531548727 | $279.99 | 0 | PlayStation 4 Pro 1TB Limited Edition Console - Death Stranding |
| Culpeper | 398221129924 | $279.99 | 0 | Pokemon Emerald Version (Nintendo Game Boy Advance 2005) Dry Battery |
| Culpeper | 397582882154 | $279.99 | 0 | Blessing B-202 Beginner/Student Alto Saxophone w/Hard Case |
| Roanoke | 307120349055 | $279.99 | 0 | Snap-on SGDMRC44FMB 44pc Ratcheting Soft Grip Screwdriver Master Set |
| Culpeper | 398200084919 | $269.99 | 0 | Cornwell Tools CTGT120 Diagnostic Thermal Imaging Camera - Automotive  |
| Culpeper | 397625159587 | $263.99 | 0 | DieHard 190 Pc Mechanics Tool Set 1/4 3/8 1/2 Drive SAE Metric Case |
| Roanoke | 298575709087 | $259.99 | 0 | SanDisk 2TB Extreme Portable USB-C USB 3.2 External SSD |
| Lexington | 157644268113 | $255.99 | 0 | Snap-On Tools CTR817 Brushless 1/4" Drive Long Reach 14.4v Ratchet W/  |
| Culpeper | 398235964930 | $249.99 | 0 | Coach CCC87 Hadley Convertible Crossbody Bag With Cow Print And Tassel |
| Lexington | 158214956104 | $249.99 | 0 | Bosch GLL 150 E Professional 360° Self-Leveling Laser Level w/ LR3 Rec |
| Roanoke | 298578599365 | $249.99 | 0 | Snap On Tools FM209EX01B Extension Set 9 Piece in Foam |
| Waynesboro | 800303619445 | $249.94 | 0 | WWE Roman Reigns Number 131 Signed Autograph Funko Pop Vinyl Figure -  |
| Culpeper | 396699630035 | $239.99 | 0 | King Baby K42-5179 Sterling Silver & Leather Large Double Wrap 17" B |
| Harrisonburg | 800232060996 | $229.99 | 0 | NINTENDO SWITCH HANDHELD - OLED - HAC-016 (VA5019380) |
| Culpeper | 397981696735 | $219.99 | 0 | Vintage "Greenbrier" By Gorham Sterling Silver 4 Tong Fork 40.5G |
| Harrisonburg | 800145552197 | $219.99 | 0 | Blink Security Outdoor 4 5 Camera System |
| Lexington | 158089430661 | $219.99 | 0 | Apple iPad Pro 12.9-inch (2nd Generation) |
| Roanoke | 307077672852 | $219.99 | 0 | Buck 498 Ergo Hunter Pro Fixed Blade Hunting Knife w/ Sheath - New in  |
| Roanoke | 306986542135 | $209.99 | 0 | Matco Tools 30pc 1/2" Dr Metric 6pt ADV Standard/Deep Impact Set / S |
| Lexington | 157644268053 | $207.99 | 0 | Snap-On CTQ861 MicroLithium 14.4V 1/4" Hex Cordless Brushless Impact D |
| Lexington | 158119170062 | $200.00 | 0 | GoPro HERO11 Black Mini 5.3K Action Camera Bundle Case Tripod Mounts T |

_...and 75 more, full list in specifics_candidates.json_