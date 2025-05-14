# 💻 Inkochain Bot

## General information

Software for processing main modules in Inkochain.

## Main Features

* **Proxy support**
* **Ability to choose the module to be executed**
* **Asynchronous OOP code**
* **EIP-1559**

## 🧩 Modules
### _Bridges_
1. _Bridge Relay from Ink to Optimism_
2. _Bridge Relay from Ink to Base_
3. _Bridge Relay from Base to Ink_
4. _Bridge Relay from Optimism to Ink_
5. _Bridge Owlto from Ink to Optimism_
6. _Bridge Owlto from Ink to Base_
7. _Bridge Owlto from Base to Ink_
8. _Bridge Owlto from Optimism to Ink_
9. _Bridge BridgeGG from Ethereum Mainnet to Ink_

### _Others_
10. _Claim Daily GM_
11. _Claim ZNS Domen_
12. _Mint Paragraph NFT (Optimism Network only)_


## 📄Ввод своих данных

### All necessary data should be specified in the `config/data` folder.
   1. **Private Key** - private keys
   2. **Proxy** - proxy for each account

## ⚙️ Software customization `config/settings.yaml`
```yaml
# Controls asyncronious execution
threads: 10

# Shuffle accounts before execution
shuffle_flag: true

# Initial delay range before starting operations (seconds)
delay_before_start:
    min: 1
    max: 10

# Delay between tasks (seconds)
delay_between_tasks:
    min: 60
    max: 300

percent_amount: # what percent of balance you want to bridge, swap and so on ...
    - min: 50
    - max: 75

save_amount: # what amount in Ether you want to leave in source network
    - min: 0.001
    - max: 0.002

# Optional
# Individual Modules configuration

#  - bridge_owlto_op_to_ink
#  - bridge_owlto_base_to_ink
#  - bridge_owlto_ink_to_op
#  - bridge_owlto_ink_to_base
#  - bridge_relay_op_to_ink
#  - bridge_relay_base_to_ink
#  - bridge_relay_ink_to_op
#  - bridge_relay_ink_to_base
#  - bridge_gg_ethereum_to_ink
#  - mint_paragraf_nft
#  - buy_znc_domen_ink_network
#  - claim_daily_gm

# Example:
module_settings:
    bridge_relay_ink_to_op:
        percent_range:
            min: 45
            max: 80
        save_amount:
            # Fixed amount
            min: 0.001
            max: 0.001

```

## 🛠️ Installing and launching the project

> By installing the project, you accept the risks of using the software

Once you download the project, **make sure** that you have Python 3.12.7

1. __Installing a virtual environment__

```bash
  python -m venv ./venv
```

2. __To install the necessary libraries, type in the console__

```bash
  pip install -r requirements.txt
```

3. __Launch by command__
```bash
python main.py
```

## ❔ Where do I write my question?

- [@degensoftware](https://t.me/degensoftware) - my channel
- [@degen_software](https://t.me/degen_software) - answers to any question

## ❤️‍🔥Donate (Any EVM)

### `0x5b7aa8714fa6784652518f6a08db986a0811c2b1`
> Thank you for your support❤️
