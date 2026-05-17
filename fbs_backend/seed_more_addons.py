# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.models import (
    Airline, BaggageOption, MealOption, MealCategory,
    AssistanceService, TravelInsurancePlan, InsuranceProvider,
    InsuranceBenefit, InsuranceCoverageType, PlanCoverage
)

def seed_more_addons():
    print("=" * 60)
    print("SEEDING MORE ADD-ON DATA")
    print("=" * 60)

    # ── Meal Categories ──────────────────────────────────────────
    main_course, _  = MealCategory.objects.get_or_create(name='Main Course',  defaults={'display_order': 1})
    beverage, _     = MealCategory.objects.get_or_create(name='Beverages',    defaults={'display_order': 2})
    light_meal, _   = MealCategory.objects.get_or_create(name='Light Meals',  defaults={'display_order': 3})
    snacks, _       = MealCategory.objects.get_or_create(name='Snacks',       defaults={'display_order': 4})
    desserts, _     = MealCategory.objects.get_or_create(name='Desserts',     defaults={'display_order': 5})
    print("✅ Meal categories ready.")

    # ── Airline IDs (match actual DB) ───────────────────────────
    CEB_ID = 1   # Cebu Pacific  (5J)
    PR_ID  = 2   # Philippine Airlines (PR)
    AA_ID  = 3   # AirAsia Philippines (Z2)

    airlines = Airline.objects.filter(id__in=[PR_ID, CEB_ID, AA_ID])
    airline_map = {a.id: a for a in airlines}

    for aid, label in [(CEB_ID, 'Cebu Pacific'), (PR_ID, 'PAL'), (AA_ID, 'AirAsia')]:
        if aid not in airline_map:
            print(f"Warning: Airline ID {aid} ({label}) not found - skipping.")

    # ═══════════════════════════════════════════════════════════════
    # PHILIPPINE AIRLINES (PR)
    # ═══════════════════════════════════════════════════════════════
    if PR_ID in airline_map:
        pr = airline_map[PR_ID]
        print(f"\n── Philippine Airlines (PR) ──")

        # Extra Baggage
        baggage_pr = [
            (5,  600,  '5kg Extra Baggage'),
            (10, 800,  '10kg Extra Baggage'),
            (15, 1150, '15kg Extra Baggage'),
            (20, 1400, '20kg Extra Baggage'),
            (25, 1750, '25kg Extra Baggage'),
            (30, 2000, '30kg Extra Baggage'),
            (40, 2600, '40kg Extra Baggage'),
        ]
        for w, p, n in baggage_pr:
            obj, created = BaggageOption.objects.get_or_create(
                airline=pr, weight_kg=w,
                defaults={'name': n, 'price': p, 'display_order': w}
            )
            print(f"  {'✚' if created else '–'} Baggage {n} ₱{p}")

        # Meals
        meals_pr = [
            ('Filipino Favorite - Chicken Adobo', 'Tender chicken marinated in soy and vinegar, served with garlic rice.',          'standard',   main_course, 450, 1),
            ("Cattleman's Roast Beef",            'Slow-roasted beef with mushroom gravy and mashed potatoes.',                     'standard',   main_course, 550, 2),
            ('Seafood Pasta with White Wine Sauce','Fresh catch in a light creamy sauce.',                                           'standard',   main_course, 480, 3),
            ('Lamb Kare-Kare',                    'Tender lamb in rich peanut sauce with vegetables.',                               'standard',   main_course, 580, 4),
            ('Bangus Sisig',                      'Crispy milkfish sisig with garlic rice and calamansi.',                           'standard',   main_course, 430, 5),
            ('Vegetarian Kare-Kare',              'Mixed vegetables in peanut sauce with bagoong on the side.',                     'vegetarian', main_course, 380, 6),
            ('Vegan Tofu Stir-Fry',              'Silken tofu with seasonal vegetables in ginger-soy glaze.',                       'vegan',      light_meal,  340, 7),
            ('Halal Chicken Biryani',             'Fragrant basmati rice with tender halal chicken and spiced gravy.',              'halal',      main_course, 460, 8),
            ('Child Pasta Marinara',              'Simple tomato pasta with mild seasoning, perfect for young flyers.',              'child',      light_meal,  280, 9),
            ('Fresh Tropical Fruit Platter',      'Seasonal sliced fruits — mango, papaya, pineapple.',                             'vegan',      snacks,      220, 10),
            ('Mango Bravo Cake Slice',            'Signature PAL mango-cream cake dessert.',                                         'standard',   desserts,    250, 11),
            ('Mineral Water 500ml',               'Still mineral water.',                                                            'vegan',      beverage,    80,  12),
            ('Freshly Brewed Coffee',             'Premium Philippine brew — arabica blend.',                                         'standard',   beverage,    120, 13),
            ('Buko Pandan Shake',                 'Refreshing young coconut with pandan jelly.',                                     'vegan',      beverage,    150, 14),
        ]
        for name, desc, mtype, cat, price, order in meals_pr:
            obj, created = MealOption.objects.get_or_create(
                airline=pr, name=name,
                defaults={'description': desc, 'meal_type': mtype, 'category': cat,
                          'price': price, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Meal: {name}")

        # Assistance
        assist_pr = [
            ('PAL Wheelchair Assistance',         'wheelchair',          'standard', 'Full gate-to-aircraft wheelchair assistance.',         0.00,    True,  48, 1),
            ('Mabuhay Lounge Access',             'boarding',            'premium',  'Exclusive lounge access at major terminals.',           1200.00, False, 24, 2),
            ('PAL Medical Assistance',            'medical',             'standard', 'Onboard nurse escort and oxygen support.',              0.00,    True,  72, 3),
            ('Unaccompanied Minor Service (PAL)', 'unaccompanied_minor', 'standard', 'Dedicated escort for children traveling alone (5–11).',  800.00,  False, 72, 4),
            ('Pet-in-Cabin (PAL)',                'pet',                 'basic',    'Travel with small pets in approved carriers.',           1500.00, False, 48, 5),
            ('Priority Boarding (PAL)',           'boarding',            'basic',    'Board ahead of general boarding groups.',               400.00,  False, 0,  6),
        ]
        for name, stype, level, desc, price, included, notice, order in assist_pr:
            obj, created = AssistanceService.objects.get_or_create(
                airline=pr, name=name,
                defaults={'service_type': stype, 'level': level, 'description': desc,
                          'price': price, 'is_included': included,
                          'requires_advance_notice': notice, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Assistance: {name}")

    # ═══════════════════════════════════════════════════════════════
    # CEBU PACIFIC (5J)
    # ═══════════════════════════════════════════════════════════════
    if CEB_ID in airline_map:
        ceb = airline_map[CEB_ID]
        print(f"\n── Cebu Pacific (5J) ──")

        baggage_ceb = [
            (10, 450,  '10kg Prepaid Baggage'),
            (15, 550,  '15kg Prepaid Baggage'),
            (20, 650,  '20kg Prepaid Baggage'),
            (24, 850,  '24kg Prepaid Baggage'),
            (28, 1150, '28kg Prepaid Baggage'),
            (32, 1450, '32kg Prepaid Baggage'),
        ]
        for w, p, n in baggage_ceb:
            obj, created = BaggageOption.objects.get_or_create(
                airline=ceb, weight_kg=w,
                defaults={'name': n, 'price': p, 'display_order': w}
            )
            print(f"  {'✚' if created else '–'} Baggage {n} ₱{p}")

        meals_ceb = [
            ('Beef Pares with Garlic Rice',   'Classic Filipino beef stew with savory-sweet sauce.',                'standard',   main_course, 350, 1),
            ('Chicken Sisig Meal',            'Spicy minced chicken with calamansi, topped on rice.',              'standard',   main_course, 350, 2),
            ('Pork Longganisa Platter',       'Sweet pork sausage with sinangag and itlog.',                       'standard',   main_course, 320, 3),
            ('Vegetable Salpicao (V)',        'Sautéed mushrooms with garlic and bell peppers.',                   'vegetarian', light_meal,  280, 4),
            ('Tuna Sandwich (Light)',         'Classic tuna salad on wheat bread with pickle.',                    'standard',   light_meal,  240, 5),
            ('Palabok Cup',                   'Thick rice noodles with shrimp-pork sauce and toppings.',           'standard',   snacks,      280, 6),
            ('Halal Chicken Curry',           'Halal-certified mild chicken curry with steamed rice.',             'halal',      main_course, 370, 7),
            ('Vegan Mongo Soup Set',          'Mung bean soup with kangkong, served with plain rice.',             'vegan',      light_meal,  260, 8),
            ("Kid's Spaghetti Meal",          'Sweet-style spaghetti with hotdog, child portion.',                'child',      light_meal,  220, 9),
            ('Banana Chocolate Muffin',       'Moist banana muffin with dark chocolate chips.',                   'standard',   snacks,      150, 10),
            ('C2 Green Tea 350ml',            'Ready-to-drink green tea, lightly sweetened.',                     'vegan',      beverage,    80,  11),
            ('Hot Brewed Coffee (5J)',        'Freshly brewed medium-roast coffee.',                              'standard',   beverage,    100, 12),
            ('Choco Loco Shake',             'Chocolate milk shake — a passenger favorite.',                      'standard',   beverage,    130, 13),
        ]
        for name, desc, mtype, cat, price, order in meals_ceb:
            obj, created = MealOption.objects.get_or_create(
                airline=ceb, name=name,
                defaults={'description': desc, 'meal_type': mtype, 'category': cat,
                          'price': price, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Meal: {name}")

        assist_ceb = [
            ('CEB Wheelchair Service',            'wheelchair',          'standard', 'Assistance for passengers with reduced mobility.',         0.00,   True,  48, 1),
            ('CEB Priority Boarding',             'boarding',            'basic',    'Board first before general passengers.',                  350.00, False, 0,  2),
            ('Unaccompanied Minor (CEB)',         'unaccompanied_minor', 'standard', 'Escort service for unaccompanied children aged 5–11.',    700.00, False, 48, 3),
            ('CEB Medical Travel Clearance',     'medical',             'standard', 'Coordination of medical documents for special needs pax.', 0.00,   True,  72, 4),
            ('Pet-in-Hold (CEB)',                'pet',                 'basic',    'Pets transported in the cargo hold in approved carriers.', 1200.00,False, 48, 5),
        ]
        for name, stype, level, desc, price, included, notice, order in assist_ceb:
            obj, created = AssistanceService.objects.get_or_create(
                airline=ceb, name=name,
                defaults={'service_type': stype, 'level': level, 'description': desc,
                          'price': price, 'is_included': included,
                          'requires_advance_notice': notice, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Assistance: {name}")

    # ═══════════════════════════════════════════════════════════════
    # AIRASIA PHILIPPINES (Z2)
    # ═══════════════════════════════════════════════════════════════
    if AA_ID in airline_map:
        aa = airline_map[AA_ID]
        print(f"\n── AirAsia Philippines (Z2) ──")

        baggage_aa = [
            (15, 450,  '15kg Value Baggage'),
            (20, 550,  '20kg Value Baggage'),
            (25, 750,  '25kg Value Baggage'),
            (30, 950,  '30kg Value Baggage'),
            (40, 1350, '40kg Value Baggage'),
        ]
        for w, p, n in baggage_aa:
            obj, created = BaggageOption.objects.get_or_create(
                airline=aa, weight_kg=w,
                defaults={'name': n, 'price': p, 'display_order': w}
            )
            print(f"  {'✚' if created else '–'} Baggage {n} ₱{p}")

        meals_aa = [
            ("Pak Nasser's Nasi Lemak",       'Coconut rice with spicy sambal, rendang and egg.',                 'standard',   main_course, 250, 1),
            ("Uncle Chin's Chicken Rice",     'Hainanese-style chicken rice with ginger sauce.',                  'standard',   main_course, 250, 2),
            ('Korean Bibimbap Bowl',          'Rice topped with sautéed vegetables and gochujang sauce.',         'vegetarian', main_course, 280, 3),
            ('Hotdog Noodle Combo',           'Instant noodles with sausage—a budget traveler classic.',          'standard',   light_meal,  180, 4),
            ('Tuna Onigiri',                  'Japanese-style rice ball with tuna mayo filling.',                 'standard',   snacks,      130, 5),
            ('Veggie Sushi Roll (6 pcs)',     'Cucumber and avocado maki, served with soy sauce.',               'vegan',      snacks,      200, 6),
            ('Halal Beef Rendang Rice',       'Tender beef slow-cooked in coconut and spices, halal-certified.', 'halal',      main_course, 280, 7),
            ("Kid's Chicken Nuggets Set",    '5 golden chicken nuggets with ketchup and fries.',                 'child',      light_meal,  200, 8),
            ('Chocolate Lava Cake',          'Warm chocolate cake with gooey center.',                           'standard',   desserts,    150, 9),
            ('Chendol Cup',                  'Malaysian shaved ice dessert with coconut milk and palm sugar.',   'vegan',      desserts,    130, 10),
            ('100PLUS Isotonic Drink',       'Hydrating isotonic drink, lemon-lime flavour.',                   'vegan',      beverage,    80,  11),
            ('Milo Hot Drink',               'Classic chocolate malt hot drink.',                               'standard',   beverage,    90,  12),
            ('AirAsia Kopi O',              'Traditional Malaysian black coffee, served hot.',                   'vegan',      beverage,    80,  13),
        ]
        for name, desc, mtype, cat, price, order in meals_aa:
            obj, created = MealOption.objects.get_or_create(
                airline=aa, name=name,
                defaults={'description': desc, 'meal_type': mtype, 'category': cat,
                          'price': price, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Meal: {name}")

        assist_aa = [
            ('Xpress Boarding Service',          'boarding',            'basic',    'Skip the line and board first.',                          400.00, False, 0,  1),
            ('AirAsia Wheelchair Assistance',    'wheelchair',          'standard', 'Airport wheelchair assistance for all zones.',              0.00,  True,  48, 2),
            ('Unaccompanied Minor (AirAsia)',    'unaccompanied_minor', 'standard', 'Escorted travel for children aged 4–12.',                  650.00, False, 48, 3),
            ('AirAsia Medical Clearance',        'medical',             'standard', 'Assistance for passengers with medical conditions.',         0.00,  True,  72, 4),
            ('BIG Comfort Kit',                  'other',               'premium',  'Blanket, pillow, eye mask and earplugs set.',               350.00, False, 0,  5),
        ]
        for name, stype, level, desc, price, included, notice, order in assist_aa:
            obj, created = AssistanceService.objects.get_or_create(
                airline=aa, name=name,
                defaults={'service_type': stype, 'level': level, 'description': desc,
                          'price': price, 'is_included': included,
                          'requires_advance_notice': notice, 'display_order': order}
            )
            print(f"  {'✚' if created else '–'} Assistance: {name}")

    # ═══════════════════════════════════════════════════════════════
    # TRAVEL INSURANCE PLANS
    # ═══════════════════════════════════════════════════════════════
    print(f"\n── Travel Insurance Plans ──")

    prov_allianz, _ = InsuranceProvider.objects.get_or_create(
        code='ALLIANZ',
        defaults={'name': 'Allianz Travel Insurance', 'default_commission_rate': 15.00}
    )
    prov_axa, _ = InsuranceProvider.objects.get_or_create(
        code='AXA',
        defaults={'name': 'AXA Philippines', 'default_commission_rate': 15.00}
    )
    prov_aig, _ = InsuranceProvider.objects.get_or_create(
        code='AIG',
        defaults={'name': 'AIG Travel Guard', 'default_commission_rate': 15.00}
    )
    prov_coc, _ = InsuranceProvider.objects.get_or_create(
        code='COC',
        defaults={'name': 'Cocogen Insurance', 'default_commission_rate': 12.00}
    )

    # Collect all airline objects that exist
    all_airlines = list(airline_map.values())
    pr_and_ceb   = [a for a in all_airlines if a.id in [PR_ID, CEB_ID]]
    aa_only      = [a for a in all_airlines if a.id in [AA_ID]]

    insurance_plans = [
        # provider, name, description, retail, wholesale, days, plan_type, airlines_list, order
        (prov_allianz, 'Allianz Basic Cover',
         'Essential travel protection covering emergency medical up to ₱500,000, flight delays, and lost baggage.',
         299.00, 220.00, 30, 'basic', all_airlines, 1),

        (prov_allianz, 'Allianz Standard Shield',
         'Comprehensive cover with ₱1,000,000 medical, trip cancellation, baggage loss, and personal accident.',
         599.00, 450.00, 45, 'standard', all_airlines, 2),

        (prov_allianz, 'Allianz Premium Guard',
         'Premium protection: ₱3,000,000 medical, unlimited evacuation, adventure sports cover, and concierge.',
         999.00, 750.00, 60, 'premium', all_airlines, 3),

        (prov_axa, 'AXA SmartTravel Lite',
         'Affordable cover for domestic trips — medical emergencies up to ₱300,000 and delayed baggage.',
         199.00, 150.00, 30, 'basic', pr_and_ceb, 4),

        (prov_axa, 'AXA SmartTravel Plus',
         'Wider protection for regional travel: ₱2,000,000 medical, trip cancellation, and 24/7 hotline.',
         799.00, 600.00, 45, 'standard', pr_and_ceb, 5),

        (prov_axa, 'AXA Comprehensive Explorer',
         'Top-tier plan for frequent flyers: ₱5,000,000 medical, pre-existing conditions, and sports activities.',
         1299.00, 980.00, 90, 'comprehensive', all_airlines, 6),

        (prov_aig, 'AIG Travel Guard Essential',
         'Entry-level plan with ₱500,000 medical, emergency evacuation, and missed connection cover.',
         349.00, 260.00, 30, 'basic', aa_only, 7),

        (prov_aig, 'AIG Travel Guard Plus',
         'Mid-tier plan: ₱1,500,000 medical, baggage delay, trip interruption, and 24/7 emergency line.',
         699.00, 520.00, 45, 'standard', aa_only, 8),

        (prov_coc, 'Cocogen DomesticCare Basic',
         'Affordable domestic travel cover: ₱250,000 personal accident and flight delay compensation.',
         149.00, 110.00, 14, 'basic', all_airlines, 9),

        (prov_coc, 'Cocogen DomesticCare Plus',
         'Enhanced domestic protection: ₱750,000 medical, baggage loss, and trip cancellation.',
         399.00, 290.00, 30, 'standard', all_airlines, 10),
    ]

    for prov, name, desc, retail, wholesale, days, ptype, airlines_list, order in insurance_plans:
        plan, created = TravelInsurancePlan.objects.get_or_create(
            provider=prov, name=name,
            defaults={
                'description': desc,
                'retail_price': retail,
                'wholesale_price': wholesale,
                'coverage_duration_days': days,
                'plan_type': ptype,
                'seller_type': 'booking_platform',
                'display_order': order,
                'is_active': True,
            }
        )
        # Assign airlines
        if airlines_list:
            plan.airlines.set(airlines_list)
            plan.save()
        print(f"  {'✚' if created else '–'} Insurance: {name} (₱{retail})")

    print("\n" + "=" * 60)
    print("✅ All add-on data seeded successfully!")
    print("=" * 60)


if __name__ == '__main__':
    seed_more_addons()
