//:!:>moon
module StableCoin1::stable_coin1 {
    struct StableCoin1 {}

    fun init_module(sender: &signer) {
        aptos_framework::managed_coin::initialize<StableCoin1>(
            sender,
            b"XTRAA THB",
            b"xxTHB",
            2,
            false,
        );
    }
}
//<:!:moon
