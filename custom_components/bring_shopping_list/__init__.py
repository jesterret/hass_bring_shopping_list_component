import logging
from homeassistant.const import ATTR_ENTITY_ID
import aiohttp
DOMAIN = 'bring_shopping_list'

_LOGGER = logging.getLogger(DOMAIN)

SPEC = 'specification'

async def async_setup(hass, config):
    async def handle_swap_item(call):
        async def put(url, data):
            async with aiohttp.ClientSession() as session:
                async with session.put(url, data=data):
                    pass

        name = call.data.get('key')
        entity = call.data.get('entityId')
        states = hass.states.get(entity).attributes

        purchases = { x['key'] : x for x in states['Purchase']}
        recents = { x['key'] : x for x in states['Recently']}

        item = ('recently', purchases) if name in purchases else ('purchase', recents)

        entry = item[1][name] if name in item[1] else {'key': name}
        data = {'uuid': states['List_Id']}
        data[item[0]] = entry['key']
        if SPEC in entry:
            data[SPEC] = entry[SPEC]

        url = f"https://api.getbring.com/rest/bringlists/{data['uuid']}"
        await put(url, data)
        await hass.services.async_call('homeassistant', 'update_entity', { ATTR_ENTITY_ID: [entity]})

    bring = config[DOMAIN]
    hass.services.async_register(DOMAIN, 'swap_item', handle_swap_item)
    hass.helpers.discovery.load_platform('sensor', DOMAIN, bring, config)

    return True

    # print(config)
    #hass.states.async_set('bring.world', 'Earth')
    #hass.states.async_set('bring.purchase', 'Alufolie,Tampons')
    #hass.data[DOMAIN] = {'temperature': 23}

    #component = hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass, SCAN_INTERVAL)
    # await component.async_setup(config)
